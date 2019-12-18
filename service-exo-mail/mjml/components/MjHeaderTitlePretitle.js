import { registerDependencies } from 'mjml-validator'
import { BodyComponent } from 'mjml-core'

registerDependencies({
  // Tell the validator which tags are allowed as our component's parent
  'mj-body': ['mj-header-title-pretitle'],
  'mj-wrapper': ['mj-header-title-pretitle'],
  // Tell the validator which tags are allowed as our component's children
  'mj-header-title-pretitle': []
})

export default class MjHeaderTitlePretitle extends BodyComponent {
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
    'background-color': '#001846'
  }

  // This functions allows to define styles that can be used when rendering (see render() below)
  getStyles() {
    return {
      contentDiv: {
        'padding': "0"
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
        <mj-text color="#FFCA75" font-size="14px" font-weight="700" line-height="21px" letter-spacing="4px" text-transform="uppercase">
          ${this.getAttribute('pre-title')}
        </mj-text>
        <mj-text color="white" font-size="32px" font-weight="700" line-height="48px">
          ${this.getAttribute('title')}
        </mj-text>
        <mj-spacer height="20px"/>
        </mj-column>
      </mj-section>
		`
    )}
}
