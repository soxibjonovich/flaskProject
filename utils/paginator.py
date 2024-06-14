def paginate(data, page: int, items_per_page: int):
    """
    Paginate the given dataset.

    :param data: List of items to paginate.
    :param page: Current page number.
    :param items_per_page: Number of items per page.
    :return: A tuple containing the paginated data, the current page number, and the total number of pages.
    """
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_data = data[:end]
    total_pages = (len(data) + items_per_page - 1) // items_per_page
    return paginated_data, page, total_pages
