<%!
    import six
    import markupsafe
    from pyramid_admin2.helpers import cell_datatype
    from pyramid_admin2 import model as model_hepler, resources as _rsr
    def get_layout_file(context):
        try:
            return context['main_template'].uri
        except KeyError:
            return None
%>
<%inherit file="${get_layout_file(context)}"/>

<style type="text/css">
.table-objects td, .object-detail .value {font-family: Monaco,Menlo,Consolas,"Courier New",monospace; font-size:90%;}
td.datatype-number {text-align: right}
td.datatype-datetime {text-align: right}
.datatype-bool {font-weight: bold; font-style: italic}
.deform input, .deform textarea, .deform select {font-family: monospace}
</style>

<%block name="flashes_block">
<% messages = request.session.pop_flash('pbackend') %>
% if messages:
    % for message in messages:
        <div class="alert alert-success">${message}</div>
    % endfor
% endif
</%block>

<%def name="cmd_button(cmd)">
<a href="${cmd['url']}"
    title="${cmd['label']}"
    % if 'onclick' in cmd and cmd['onclick']:
    onclick="${cmd['onclick']|n}"
    % endif
        ><span class="glyphicon glyphicon-${cmd.get('icon', 'usd') or 'usd'}"></span></a>
</%def>

<%def name="data_cell(val)">
% if isinstance(val, (list, tuple, set)):
    <ul class="list-unstyled">
        % for a_val in val:
            <li>${data_cell(a_val)}</li>
        % endfor
    </ul>
% else:
    <%
    val_type = cell_datatype(val)
    raw_val = val
    val = six.text_type(markupsafe.escape(raw_val))
    if val_type == 'longtext':
        val = '<br>'.join(val.splitlines())
    elif val_type == 'none':
        val = '<code>' + val + '</code>'
    elif val_type == 'bool':
        val = '<span class="label label-success">True</span>' if raw_val else \
            '<span class="label label-default">False</span>'
    elif model_hepler.is_registered_model(raw_val):
        val = '<a href="%s">%s</a>' % (_rsr.object_url(request, raw_val), val)
    %>
    ${val|n}
% endif
</%def>

<%block name="breadcrumbs">
<% entries = view.breadcrumbs %>
% if len(entries):
<ul class="breadcrumb">
% for e in entries:
    % if isinstance(e, six.string_types):
        <li class="active">${e}</li>
    % else:
    <li><a href=${e['url']}>${e['label']}</a></li>
    % endif
% endfor
</ul>
% endif
</%block>

<%block name="page_header">
<legend>
    <%block name="page_title">There's no title here</%block>
    <small>
      <div class="pull-right">
      % for cmd in view.toolbar_actions:
        ${cmd_button(cmd)}
      % endfor
      </div>
    </small>
</legend>
</%block>

${next.body()}

<script type="text/javascript">
jQuery(function ($) {
    $('form.deform button[name=cancel]').click(function (e) {
        history.go(-1)
    })
})
</script>