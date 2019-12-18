# exo-mjml

Custom components created by OpenExO.

## Getting started

A step-by-step tutorial is available [here](https://medium.com/mjml-making-responsive-email-easy/tutorial-creating-your-own-component-with-mjml-4-1c0e84e97b36).

* Clone the repo
* `npm install` inside
* Add your component inside `components` folder
* Add your component to the registrations in gulpfile.babel.js
* Use your own component in `index.mjml`
* `npm run build` to build, or `npm start` if you want to watch recompile on change you make (to your component or to `index.mjml`)
* The result will be outputted in `index.html`


## Later use of your component

### In Node.js
```
import mjml2html from 'mjml'
import { registerComponent } from 'mjml-core'
import MyComponent from './components/MyComponent'

registerComponent(MyComponent)

const { html, errors } = mjml2html(mjmlString)
```

### With the cli

Using ./mjml file


### With Docker

## To build
```
docker build -t exo-mjml .
```

## To test run
```
cat sample.mjml | docker run -i --rm exo-mjml node mjml -i -s
```

## To set as server
```
export TAG=0.9
docker run -d --name exo-mjml -p 28101:28101 exolever/exo-mjml:$TAG
```
