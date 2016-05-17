import React from 'react';
import {
    Editor,
    EditorState,
    RichUtils,
    DefaultDraftBlockRenderMap,
} from 'draft-js';

class MyEditor extends React.Component {
    constructor(props) {
        super(props);
        this.state = {editorState: EditorState.createEmpty()};
        this.onChange = (editorState) => this.setState({editorState});
        this.handleKeyCommand = (command) => this._handleKeyCommand(command);
        this.toggleBlockType = (type) => this._toggleBlockType(type);
        this.toggleInlineStyle = (style) => this._toggleInlineStyle(style);
    }

    _handleKeyCommand(command) {
        const {editorState} = this.state;
        const newState = RichUtils.handleKeyCommand(editorState, command);
        if (newState) {
            this.onChange(newState);
            return true;
        }
        return false;
    }

    _toggleBlockType(blockType) {
        this.onChange(
            RichUtils.toggleBlockType(
                this.state.editorState,
                blockType
            )
         );
    }

    _toggleInlineStyle(inlineStyle) {
        this.onChange(
            RichUtils.toggleInlineStyle(
                this.state.editorState,
                inlineStyle
            )
        );
    }

    render() {
        const { editorState } = this.state;

        let className = 'RichEditor-editor';
        var contentState = editorState.getCurrentContent();
        if (!contentState.hasText()) {
            if (contentState.getBlockMap().first().getType() !== 'unstyled') {
                className += ' RichEditor-hidePlaceholder';
            }
        }
        return (
            <div className="RichEditor-root">
                <BlockStyleControls
                        editorState={editorState}
                        onToggle={this.toggleBlockType}
                />
                <InlineStyleControls
                        editorState={editorState}
                        onToggle={this.toggleInlineStyle}
                />
                <div className={className} onClick={this.focus}>
                        <Editor
                          blockStyleFn={getBlockStyle}
                          customStyleMap={styleMap}
                          editorState={editorState}
                          handleKeyCommand={this.handleKeyCommand}
                          onChange={this.onChange}
                          placeholder="Tell a story..."
                          ref="editor"
                          spellCheck={true}
                        />
                </div>
            </div>
        );
    }
}

export default MyEditor
