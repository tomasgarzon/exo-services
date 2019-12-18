import { registerDependencies } from 'mjml-validator'
import { BodyComponent } from 'mjml-core'

registerDependencies({
  // Tell the validator which tags are allowed as our component's parent
  'mj-body': ['mj-header-ticket'],
  'mj-wrapper': ['mj-header-ticket'],
  'mj-column': ['mj-wrapper'],
  // Tell the validator which tags are allowed as our component's children
  'mj-header-ticket': []
})

export default class MjHeaderTicket extends BodyComponent {
  // Tell the parser that our component won't contain other mjml tags
  static endingTag = true
  static tagOmission = true
  // Tells the validator which attributes are allowed for mj-layout
  static allowedAttributes = {
    'background-color': 'color',
    'title': 'string',
    'pre-title': 'string'
  }

  // What the name suggests. Fallback value for this.getAttribute('attribute-name').
  static defaultAttributes = {
    'background-color': 'white'
  }

  // This functions allows to define styles that can be used when rendering (see render() below)
  getStyles() {
    return {
      contentDiv: {
        'padding': "20px 0 0 0"
      }
    }
  }

  /*
    Render is the only required function in a component.
    It must return an html string.
  */
  render() {
    return this.renderMJML(`
      <mj-section ${this.htmlAttributes({ // this.htmlAttributes() is the recommended way to pass attributes to html tags
        class: this.getAttribute('css-class'),
        'background-color': this.getAttribute('background-color'),
        style: 'contentDiv' // This will add the 'wrapperDiv' attributes from getStyles() as inline style
      })}
      >
        <mj-column>
        <mj-spacer height="20px"/>
        <mj-text font-size="14px" color="#6f23ff" font-weight="500" font-style="normal" line-height="1.5" letter-spacing="4px" text-transform="uppercase">
          ${this.getAttribute('pre-title')}
        </mj-text>
        <mj-text font-size="32px" color="#46464b" font-weight="bold" font-style="normal" line-height="1.88" letter-spacing="normal">
          ${this.getAttribute('title')}
        </mj-text>
        <mj-divider border-width="1px" border-color="rgba(70, 70, 75, 0.16)" />
        </mj-column>
      </mj-section>
		`
    )}
}
