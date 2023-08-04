def paginate(text: str, split_on='\n', max_len=900) -> list[str]:
    if split_on:
        chunks = text.split(split_on)
    else:
        chunks = list(text)
    pages = []
    curr_page = ""
    for chunk in chunks:
        if len(curr_page) + len(chunk) + len(split_on) > max_len:
            pages.append(curr_page)
            curr_page = ""

        if curr_page:
            curr_page += split_on

        curr_page += chunk
    if curr_page:
        pages.append(curr_page)

    return pages
