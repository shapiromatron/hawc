import React, { Component } from 'react';


class Wysihtml5 extends Component {
  render() {
    return (
        <ul className='wysihtml5-toolbar'>
            <li className='dropdown'>
                <a className='btn dropdown-toggle' data-toggle='dropdown' href='#'>
                    <i className='icon-font'></i>
                    &nbsp;<span className='current-font'>Normal text</span>
                &nbsp;<b className='caret'></b>
                </a>
                <ul className='dropdown-menu'>
                    <li><a data-wysihtml5-command='formatBlock' data-wysihtml5-command-value='div' tabindex='-1' href='javascript:;' unselectable='on'>Normal text</a></li>
                    <li><a data-wysihtml5-command='formatBlock' data-wysihtml5-command-value='h1' tabindex='-1' href='javascript:;' unselectable='on'>Heading 1</a></li>
                    <li><a data-wysihtml5-command='formatBlock' data-wysihtml5-command-value='h2' tabindex='-1' href='javascript:;' unselectable='on'>Heading 2</a></li>
                    <li><a data-wysihtml5-command='formatBlock' data-wysihtml5-command-value='h3' tabindex='-1' href='javascript:;' unselectable='on'>Heading 3</a></li>
                </ul>
            </li>
            <li>
                <div className='btn-group'>
                    <a className='btn' data-wysihtml5-command='bold' title='CTRL+B' tabindex='-1' href='javascript:;' unselectable='on'>Bold</a>
                    <a className='btn' data-wysihtml5-command='italic' title='CTRL+I' tabindex='-1' href='javascript:;' unselectable='on'>Italic</a>
                    <a className='btn' data-wysihtml5-command='underline' title='CTRL+U' tabindex='-1' href='javascript:;' unselectable='on'>Underline</a>
                    <a className='btn' data-wysihtml5-command='superscript' title='Superscript' tabindex='-1' href='javascript:;' unselectable='on'>x<sup>2</sup></a>
                    <a className='btn' data-wysihtml5-command='subscript' title='Subscript' tabindex='-1' href='javascript:;' unselectable='on'>x<sub>2</sub></a>
                </div>
            </li>
            <li>
                <div className='btn-group'>
                    <a className='btn' data-wysihtml5-command='insertUnorderedList' title='Unordered list' tabindex='-1' href='javascript:;' unselectable='on'><i className='icon-list'></i></a>
                    <a className='btn' data-wysihtml5-command='insertOrderedList' title='Ordered list' tabindex='-1' href='javascript:;' unselectable='on'><i className='icon-th-list'></i></a>
                    <a className='btn' data-wysihtml5-command='Outdent' title='Outdent' tabindex='-1' href='javascript:;' unselectable='on'><i className='icon-indent-right'></i></a>
                    <a className='btn' data-wysihtml5-command='Indent' title='Indent' tabindex='-1' href='javascript:;' unselectable='on'><i className='icon-indent-left'></i></a>
                </div>
            </li>
            <li>
                <div className='btn-group'>
                    <a className='btn' data-wysihtml5-action='change_view' title='Edit HTML' tabindex='-1' href='javascript:;' unselectable='on'><i className='icon-pencil'></i></a>
                </div>
            </li>
            <li>
                <div className='bootstrap-wysihtml5-insert-link-modal modal hide fade'>
                    <div className='modal-header'>
                        <a className='close' data-dismiss='modal'>×</a>
                        <h3>Insert link</h3>
                    </div>

                    <div className='modal-footer'>
                        <a href='#' className='btn' data-dismiss='modal'>Cancel</a>
                        <a href='#' className='btn btn-primary' data-dismiss='modal'>Insert link</a>
                    </div>
                </div>
                <a className='btn' data-wysihtml5-command='createLink' title='Insert link' tabindex='-1' href='javascript:;' unselectable='on'>
                    <i className='icon-share'></i>
                </a>
            </li>
            <li>
                <div className='bootstrap-wysihtml5-insert-image-modal modal hide fade'>
                    <div className='modal-header'>
                        <a className='close' data-dismiss='modal'>×</a>
                        <h3>Insert image</h3>
                    </div>

                    <div className='modal-footer'>
                        <a href='#' className='btn' data-dismiss='modal'>Cancel</a>
                        <a href='#' className='btn btn-primary' data-dismiss='modal'>Insert image</a>
                    </div>
                </div>
                <a className='btn' data-wysihtml5-command='insertImage' title='Insert image' tabindex='-1' href='javascript:;' unselectable='on'>
                    <i className='icon-picture'></i>
                </a>
            </li>
        </ul>);
  }
}

export default Wysihtml5;
