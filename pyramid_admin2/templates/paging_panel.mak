<ul class="pager">
    <li>${criteria.page_status or 'unknown current page status'}</li>
    % if criteria.previous_page_url:
        <li class=""><a href="${criteria.previous_page_url}">Previous</a></li>
    % else:
        <li class="disabled"><a href="#">Previous</a></li>
    % endif
    % if criteria.next_page_url:
        <li class=""><a href="${criteria.next_page_url}">Next</a></li>
    % else:
        <li class="disabled"><a href="#">Next</a></li>
    % endif
    % if criteria.objects_count:
    <li>Total <em>${criteria.objects_count or 'unknown'}</em> records</li>
    % endif
</ul>
