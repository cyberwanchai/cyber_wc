"""
Chat Widget Layout
Floating AI chat widget component accessible on all pages
"""

from dash import html, dcc


def get_chat_widget():
    """
    Create a floating chat widget component.

    Returns:
        html.Div: Complete chat widget with button and expandable window
    """
    return html.Div(
        [
            # Stores moved to root app.layout for persistence across page navigation
            # Floating chat button (visible when closed)
            html.Div(
                [
                    html.Div(
                        [
                            html.Span('💬', style={'fontSize': '24px', 'marginRight': '8px'}),
                            html.Span('AI Chat', style={'fontSize': '16px', 'fontWeight': '500'}),
                        ],
                        className='chat-button-content',
                    )
                ],
                id='chat-toggle-button',
                className='chat-toggle-button',
                n_clicks=0,
            ),
            # Chat window (visible when open)
            html.Div(
                [
                    # Chat header
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        '💬', style={'fontSize': '20px', 'marginRight': '8px'}
                                    ),
                                    html.Span(
                                        'AI Assistant',
                                        style={'fontSize': '18px', 'fontWeight': '600'},
                                    ),
                                ],
                                className='chat-header-title',
                            ),
                            html.Button(
                                '✕',
                                id='chat-close-button',
                                className='chat-close-button',
                                n_clicks=0,
                            ),
                        ],
                        className='chat-header',
                    ),
                    # Chat messages area
                    html.Div(
                        id='chat-messages-container',
                        className='chat-messages-container',
                        children=[
                            html.Div(
                                [
                                    html.P(
                                        "Hello! I'm your AI assistant. Ask me anything about Hong Kong's history, "
                                        'historic places, or cultural heritage.',
                                        className='chat-message chat-message-assistant',
                                    )
                                ],
                                className='chat-message-wrapper',
                            )
                        ],
                    ),
                    # Chat input area
                    html.Div(
                        [
                            html.Div(
                                [
                                    dcc.Input(
                                        id='chat-input',
                                        type='text',
                                        placeholder='Type your message...',
                                        className='chat-input-field',
                                        value='',
                                        debounce=False,
                                    ),
                                    html.Button(
                                        'Send',
                                        id='chat-send-button',
                                        className='chat-send-button',
                                        n_clicks=0,
                                    ),
                                ],
                                className='chat-input-container',
                            ),
                            html.Div(
                                [
                                    html.Button(
                                        'Clear Chat',
                                        id='chat-clear-button',
                                        className='chat-clear-button',
                                        n_clicks=0,
                                    )
                                ],
                                className='chat-actions-container',
                            ),
                        ],
                        className='chat-input-area',
                    ),
                    # Loading indicator (hidden by default)
                    html.Div(
                        id='chat-loading-indicator',
                        className='chat-loading-indicator',
                        style={'display': 'none'},
                        children=[
                            html.Div(className='chat-loading-spinner'),
                            html.Span('AI is thinking...', className='chat-loading-text'),
                        ],
                    ),
                ],
                id='chat-window',
                className='chat-window',
            ),
        ],
        className='chat-widget-container',
    )
