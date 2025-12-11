def build_system_message(format_style: str) -> str:
    """
    Return a system prompt that instructs the model how to format the response.
    """
    format_style = (format_style or "plain").lower()

    if format_style == "bullets":
        return (
            "You are a helpful assistant. "
            "Format your main points as clear bullet points using '-' or '•'. "
            "Use short, readable lines."
        )
    elif format_style == "numbered":
        return (
            "You are a helpful assistant. "
            "Format your main points as a numbered list (1., 2., 3., ...). "
            "Use short, readable lines."
        )
    else:
        return (
            "You are a helpful assistant. "
            "Respond in clear paragraphs that are easy to read."
        )
