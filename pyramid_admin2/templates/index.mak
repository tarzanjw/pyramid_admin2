<%!
    def get_layout_file(context):
        try:
            return context['main_template'].uri
        except KeyError:
            return None
%>
<%inherit file="${get_layout_file(context)}"/>

<legend>Registered models</legend>
<ol>
    % for m in models:
    <li><a href="${m['url']}">${m['name']}</a></li>
    % endfor
</ol>