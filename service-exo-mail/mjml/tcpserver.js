'use strict';

process.on('SIGINT', function() {
    process.exit();
});

// create a custom timestamp format for log statements
const SimpleNodeLogger = require('simple-node-logger'),
    opts = {
        logFilePath:'server.log',
        timestampFormat:'YYYY-MM-DD HH:mm:ss.SSS'
    },
log = SimpleNodeLogger.createSimpleLogger( opts );

var mjml = require('mjml'),
    mjml_maj_ver = parseInt(require('mjml/package.json').version.split('.')[0]),
    net = require('net'),
    fs = require('fs'),
    argv = process.argv.slice(2),
    conf = {
        host: '127.0.0.1',
        port: '28101',
        touchstop: null,
        mjml: {}
    };

// require your custom component here
var core = require('mjml-core')
var MjLayout = require('./lib/MjLayout').default
var MjImageText = require('./lib/MjImageText').default
var MjBasicComponent = require('./lib/MjBasicComponent').default
var MjTagList = require('./lib/MjTagList').default
var MjTagElement = require('./lib/MjTagElement').default
var MjHeaderTitlePretitle = require('./lib/MjHeaderTitlePretitle').default
var MjHeaderTicket = require('./lib/MjHeaderTicket').default

core.registerComponent(MjBasicComponent)
core.registerComponent(MjImageText)
core.registerComponent(MjLayout)
core.registerComponent(MjTagList)
core.registerComponent(MjTagElement)
core.registerComponent(MjHeaderTitlePretitle)
core.registerComponent(MjHeaderTicket)

for (var i = 0; i < argv.length; i++) {
    var kv, key, val,
        arg = argv[i];
    try {
        if (!arg.startsWith('--')) {
            throw {message: 'unknown arg'};
        } else {
            arg = arg.slice(2);
        }
        if (arg === 'help') {
            if (mjml_maj_ver >= 4) {
                // more options: https://github.com/mjmlio/mjml/blob/master/packages/mjml-core/src/index.js#L34
                console.log('Run command: NODE_PATH=node_modules node tcpserver.js ' +
                            '--port=28101 --host=127.0.0.1 --touchstop=/tmp/mjmltcpserver.stop ' +
                            '--mjml.minify=false --mjml.validationLevel=soft');
            } else {
                // more options: https://github.com/mjmlio/mjml/blob/3.3.x/packages/mjml-core/src/MJMLRenderer.js#L78
                console.log('Run command: NODE_PATH=node_modules node tcpserver.js ' +
                            '--port=28101 --host=127.0.0.1 --touchstop=/tmp/mjmltcpserver.stop ' +
                            '--mjml.disableMinify=false --mjml.level=soft');
            }
            process.exit();
        }
        kv = arg.split('=', 2);
        key = kv[0];
        val = kv[1];
        if (!key || !val) throw {message: 'wrong syntax'};
        if (conf.hasOwnProperty(key) && key !== 'mjml') {
            conf[key] = val;
        } else if (key.startsWith('mjml.')) {
            if (val === 'true') {
                val = true;
            } else if (val === 'false') {
                val = false;
            }
            conf.mjml[key.slice(5)] = val;
        } else {
            throw {message: 'unknown arg'};
        }
    } catch (err) {
        console.log('Invalid parsing arg "%s": %s', argv[i], err.message);
        process.exit(1);
    }
}

function handleConnection(conn) {
    var total_data = '',
        header_size = 9,
        data_size, result;
    conn.setEncoding('utf8');
    conn.on('data', function(d) {
        log.info('Server requested: ');
        total_data += d;
        if (total_data.length < header_size) return;
        if (data_size === undefined) data_size = parseInt(total_data.slice(0, header_size)) + header_size;
        if (total_data.length < data_size) {
            return;
        } else if (total_data.length > data_size) {
            result = 'MJML server received too many data';
            conn.write('1');
        } else {
            try {
                total_data = total_data.slice(header_size).toString();
                if (mjml_maj_ver >= 4) {
                    result = mjml(total_data, conf.mjml);
                } else {
                    result = mjml.mjml2html(total_data, conf.mjml);
                }
                if (typeof result === 'object') {
                    if (result.errors.length) throw {message: JSON.stringify(result.errors, null, 2)};
                    result = result.html;
                }
                conn.write('0');
            } catch (err) {
                result = err.message;
                conn.write('1');
            }
        }
        conn.write((Array(header_size + 1).join('0') + Buffer.byteLength(result).toString()).slice(-9));
        conn.write(result);
        log.info('Server response OK: ');
        total_data = '';
        data_size = undefined;
        result = undefined;
    });
    conn.once('close', function() {
        log.info('Server closed: ');
    });
    conn.on('error', function(err) {
        log.info('Server error: ', err);
    });
    conn.on('end', function() {});
}

var server = net.createServer();
server.on('connection', handleConnection);
server.listen(conf.port, conf.host, function () {
    log.info('RUN SERVER ', conf.host, ':', conf.port);
});

if (conf.touchstop) {
    try {
        fs.statSync(conf.touchstop);
    } catch (e) {
        fs.closeSync(fs.openSync(conf.touchstop, 'w'));
    }

    fs.watchFile(conf.touchstop, function() {
        log.info('STOP SERVER (cause touchstop)');
        server.close();
        process.exit();
    });
}

