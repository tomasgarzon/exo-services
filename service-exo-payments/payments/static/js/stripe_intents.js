(function() {
  'use strict';

  var stripe = Stripe(document.querySelector('input#stripe_public_key').value);
  var elements = stripe.elements();
  var cardElement = elements.create(
    'card',
     {
      'style': {
        'base': {
          'iconColor': '#46464b',
          'fontFamily': 'Roboto',
          'fontSize': '16px',
          'fontWeight': '400',
          'color': '#46464b',
          '::placeholder': {
            color: '#8898AA',
          }
        },
        'invalid': {
          'color': 'red',
        },
      }
    }
  );
  cardElement.mount('#card-element');

  var cardholderName = document.getElementById('payment-name');
  var notificationEmail = document.getElementById('payment-email');
  var cardButton = document.getElementById('card-button');
  var clientSecret = cardButton.dataset.secret;

  cardButton.addEventListener('click', function(event) {
    event.preventDefault();
    disableInputs();
    enableLoading();

    stripe.handleCardPayment(
      clientSecret,
      cardElement, {
        payment_method_data: {
          billing_details: {
            name: cardholderName.value,
            email: notificationEmail.value,
          }
        }
      }
    ).then(function(result) {
      if (result.error) {
        errorMessage.innerText = result.error.message;
        disableLoading();
        enableInputs();
      } else {
        location.href = 'https://www.openexo.com/payment-thank-you-page';
        disableInputs();
        successContainer.style.display = 'flex';
        successContainer.style.visibility = 'visible';
        successContainer.style.opacity = 1;
        disableLoading();
      }
    });
  });

  // Custom Form validation

  var formContainer = document.querySelector('.payment');
  var successContainer = document.querySelector('.payment_success');

  var form = formContainer.querySelector('form');

  var error = form.querySelector('.error');
  var errorMessage = error.querySelector('.message');

  cardElement.on('change', function(event) {
    if (event.error) {
      error.classList.add('visible');
      errorMessage.innerText = event.error.message;
    } else {
      error.classList.remove('visible');
      errorMessage.innerText = '';
    }
  });

  function enableLoading(){
    document.querySelector('div.loading').style.display = 'flex';
  }

  function disableLoading(){
    document.querySelector('div.loading').style.display = 'none';
  }

  function enableInputs() {
    $('#card-element').css('pointer-events', 'all');
    document.getElementById('card-button').removeAttribute('disabled');
  }

  function disableInputs() {
    $('#card-element').css('pointer-events', 'none');
    document.getElementById('card-button').setAttribute('disabled', 'true');
  }

  function addTrackingPixels(){
    addFacebookPixel();
    addGooglePixel();
  }

  function addGooglePixel(){
    var google_script = document.createElement('script');
    var transaction_id = hashCode(document.getElementById('payment-email').value);
    google_script.textContent = "gtag('event', 'conversion', { 'send_to': 'AW-721178692/z-RXCODz3acBEMSg8dcC', 'transaction_id': '" + transaction_id + "' });";
    document.getElementsByName('head')[0].appendChild(google_script);
  }

  function addFacebookPixel(){
    var amount = document.getElementById('amount').dataset.amount;
    var currency = document.getElementById('amount').dataset.currency;
    
    var fb_script = document.createElement('script');
    fb_script.textContent = '!function(f,b,e,v,n,t,s)\n' +
      '{if(f.fbq)return;n=f.fbq=function(){n.callMethod?\n' +
      'n.callMethod.apply(n,arguments):n.queue.push(arguments)};\n' +
      'if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version=\'2.0\';\n' +
      'n.queue=[];t=b.createElement(e);t.async=!0;\n' +
      't.src=v;s=b.getElementsByTagName(e)[0];\n' +
      's.parentNode.insertBefore(t,s)}(window,document,\'script\',\n' +
      '\'https://connect.facebook.net/en_US/fbevents.js\');\n' +
      'fbq(\'init\', \'1990699537703030\'); \n' +
      'fbq(\'track\', \'PageView\'); \n' +
      'fbq(\'track\', \'Purchase\', {value: ' + amount + ', currency: "' + currency + '"});';
    
    var fb_pixel = document.createElement('noscript');
    fb_pixel.textContent = '<img height="1" width="1" \n' +
      'src="https://www.facebook.com/tr?id=\'1990699537703030\'&ev=PageView\n' +
      '&noscript=1"/>';

    document.getElementsByTagName('head')[0].appendChild(fb_script);
    document.getElementsByTagName('head')[0].appendChild(fb_pixel);
  }

  function hashCode(s) {
    for(var i = 0, h = 0; i < s.length; i++)
        h = Math.imul(31, h) + s.charCodeAt(i) | 0;
    return h;
  }
})();
