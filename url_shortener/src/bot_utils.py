def escape_markdown(text):
    escape_chars = ['_', '*', '`', '[', ']']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def looks_like_url(text):
    text = text.strip()
    return text.startswith(('http://', 'https://')) and len(text) > 10

def get_success_message(short_url, original_url, is_existing):
    from messages import STATUS_MESSAGES
    
    status_message = STATUS_MESSAGES['existing'] if is_existing else STATUS_MESSAGES['new']
    
    escaped_original_url = escape_markdown(original_url)
    
    return f"""
✅ *Ссылка успешно сокращена!*

🔗 *Короткая ссылка:*
`{short_url}`

📝 *Оригинальная ссылка:*
{escaped_original_url}

{status_message}
"""