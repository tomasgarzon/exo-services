import { registerDependencies } from 'mjml-validator'
import { BodyComponent } from 'mjml-core'

registerDependencies({
  // Tell the validator which tags are allowed as our component's parent
  'mj-column': ['mj-tag-list'],
  // Tell the validator which tags are allowed as our component's children
  'mj-tag-list': []
})

/*
  Our component is a (useless) simple tag container.
*/
export default class MjTagList extends BodyComponent {

  // This functions allows to define styles that can be used when rendering (see render() below)
  getStyles() {
    return {
      wrapperDiv: {
        'padding': '10px 25px'
      }
    }
  }

  renderTag() {
    const { children } = this.props

    return `
        ${this.renderChildren(children, {
          renderer: (
            component, // eslint-disable-line no-confusing-arrow
          ) =>
            component.constructor.isRawElement()
              ? component.render()
              : `
            ${component.render()}
          `,
        })}
    `
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
          style: 'wrapperDiv' // This will add the 'wrapperDiv' attributes from getStyles() as inline style
        })}
      >
          ${this.renderTag()}
      </div>
		`
  }
}
