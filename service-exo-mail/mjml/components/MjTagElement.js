import { registerDependencies } from 'mjml-validator'
import { BodyComponent } from 'mjml-core'

registerDependencies({
  // Tell the validator which tags are allowed as our component's parent
  'mj-tag-list': ['mj-tag-element'],
  // Tell the validator which tags are allowed as our component's children
  'mj-tag': []
})

export default class MjTagElement extends BodyComponent {
  // Tell the parser that our component won't contain other mjml tags
  static endingTag = true

  // Tells the validator which attributes are allowed for mj-layout
  static allowedAttributes = {
    'color': 'color',
    'font-size': 'unit(px)',
    'background-color': 'string',
    'border-radius': 'unit(px)',
    'font-weight': 'string',
    'text-decoration': 'string'
  }

  // What the name suggests. Fallback value for this.getAttribute('attribute-name').
  static defaultAttributes = {
    color: '#46464b',
    'font-weight': 'bold',
    'border-radius': '50px',
    'background-color': 'rgba(70, 70, 75, 0.08)',
  }

  // This functions allows to define styles that can be used when rendering (see render() below)
  getStyles() {
    return {
      contentDiv: {
        'color': this.getAttribute('color'),
        'border-radius': this.getAttribute('border-radius'),
        'font-weight': this.getAttribute('font-weight'),
        'background-color': this.getAttribute('background-color'),
        'font-size': '14px',
        'line-height': '21px',
        'text-align': 'center',
        'margin-right': '10px',
        'margin-bottom': '10px',
        'float': 'left',
        'font-family': 'Roboto',
        'padding': '10px 25px',
        'text-decoration': this.getAttribute('text-decoration')
      }
    }
  }

  /*
    Render is the only required function in a component.
    It must return an html string.
  */
  render() {
    return `
      <div
        ${this.htmlAttributes({ // this.htmlAttributes() is the recommended way to pass attributes to html tags
          class: this.getAttribute('css-class'),
          style: 'contentDiv' // This will add the 'wrapperDiv' attributes from getStyles() as inline style
        })}
      >
        ${this.getContent()}
      </div>
		`
  }
}
