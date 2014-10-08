<%!
    import six
    from pyramid_admin2 import resources as _rsr
%>
<%inherit file="_layout.mak"/>
<%namespace file="_layout.mak" import="cmd_button, data_cell"/>

<%block name="page_title">${admin_mgr.display_name} list</%block>

<div class="pull-right">
    ${panel('pyramid_admin2.paging', view.criteria)}
</div>

<%block name="object_list">
<table class="table table-striped table-bordered table-condensed table-objects">
    <thead>
        <tr>
            <th>Commands</th>
            % for adc in admin_mgr.list__columns_to_display:
            <th class="">${adc.label}</th>
            % endfor
        </tr>
    </thead>
    <tbody>
    % for e in criteria.objects:
        <tr>
            <td class="col-type-commands">
                % for cmd in view.object_actions(e):
                ${cmd_button(cmd)}
                % endfor
            </td>
        % for adc in admin_mgr.list__columns_to_display:
            <%
                val_type, val = admin_mgr.get_info_to_display(e, adc)
            %>
            % if len(admin_mgr.id_attr) == 1 and adc.attr_name in admin_mgr.id_attr:
                <td class="datatype-${val_type}"><a href="${_rsr.object_url(request, e)}">${val}</a></td>
            % else:
            <td class="datatype-${val_type}">${data_cell(val)}</td>
            % endif
        % endfor
        </tr>
    % endfor
    </tbody>
</table>
</%block>

<div class="pull-right">
    ${panel('pyramid_admin2.paging', view.criteria)}
</div>