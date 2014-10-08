from pyramid_layout.panel import panel_config


@panel_config('pyramid_admin2.paging', renderer='pyramid_admin2:templates/paging_panel.mak')
def paging_panel(context, request, criteria):
    """ The panel to display paging
    :param context: the context
    :param pyramid.request.Request request: the request
    :param pyramid_admin2.admin_manager.BrowseCriteria criteria: browse/search criteria
    :return:
    """
    return {
        'criteria': criteria,
    }