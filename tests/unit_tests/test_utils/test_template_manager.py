import pytest
from unittest.mock import patch, mock_open
from app.utils.template_manager import TemplateManager


@patch("builtins.open", new_callable=mock_open, read_data="Hello {name}!")
@patch("pathlib.Path.resolve")
@patch("pathlib.Path.__truediv__")
def test_render_template(mock_truediv, mock_resolve, mock_file):
    """Test that templates are rendered with substitutions."""
    # Setup mocks
    mock_truediv.return_value = mock_truediv  # Make / operator return self for chaining
    
    # Create template manager
    template_manager = TemplateManager()
    
    # Test rendering a template with variables
    result = template_manager._read_template("any_template.md")
    
    # Verify the result
    assert result == "Hello {name}!"
    assert mock_file.called


@patch("app.utils.template_manager.TemplateManager._read_template")
@patch("markdown2.markdown")
@patch("app.utils.template_manager.TemplateManager._apply_email_styles")
def test_apply_email_styles(mock_apply_styles, mock_markdown, mock_read_template):
    """Test that email styles are applied correctly."""
    # Setup mocks
    mock_read_template.return_value = "Hello {name}!"
    mock_markdown.return_value = "<p>Hello Test User!</p>"
    mock_apply_styles.return_value = "<div style=\"font-family: Arial;\"><p>Hello Test User!</p></div>"
    
    # Create template manager
    template_manager = TemplateManager()
    
    # Test rendering with styles
    result = template_manager.render_template("email_verification", name="Test User")
    
    # Verify styles were applied
    mock_apply_styles.assert_called_once_with("<p>Hello Test User!</p>")
    assert result == "<div style=\"font-family: Arial;\"><p>Hello Test User!</p></div>"
