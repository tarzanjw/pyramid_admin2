<%!
    import markupsafe
    from pyramid_admin2 import resources as _rsr
%>
<%inherit file="_layout.mak" />
<%namespace file="_layout.mak" import="data_cell" />

<style type="text/css">
.object-detail .row {
    padding: 0 0.5em;
    border-bottom: 1px solid #eaf2fb;
}
.object-relations .row .value {border-bottom: 1px solid #eaf2fb; margin-bottom: 1em;}
.object-detail .name, .object-relations .name, .object-relations .name {
    font-weight: bold;
    text-align: right;
}
</style>
<%block name="page_title">${admin_mgr.display_name}#${obj} detail</%block>

<%block name="object_detail">
<div class="object-detail">
% for adc in admin_mgr.detail__columns_to_display:
<%
    val_type, val = admin_mgr.get_info_to_display(obj, adc)
%>
    <div class="row col-type-general">
        <div class="col-lg-3 name">${adc.label}</div>
        <div class="col-lg-9 value datatype-${val_type}">${data_cell(val)}</div>
    </div>
% endfor
</%block>
</div>
<legend>Relations</legend>
<div class="object-relations">
% for adc in admin_mgr.detail__relations_to_display:
<%
    val_type, vals = admin_mgr.get_info_to_display(obj, adc)
%>
<div class="row col-type-general">
    <div class="col-lg-3 name">${adc.label}</div>
    <div class="col-lg-9 value">
        ${data_cell(vals)}
    </div>
</div>
% endfor
</div>