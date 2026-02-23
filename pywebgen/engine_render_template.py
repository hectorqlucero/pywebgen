"""
Engine Render - Form and Grid Rendering

Matches the Clojure tabgrid implementation:
1. All grids use tabbed interface (even without subgrids)
2. First record shown by default
3. Select + New button in header
4. Vertical parent detail view
5. Subgrids with DataTables for filter/sort
"""
from typing import Optional
import random

from engine import EntityConfigManager
from engine.query import list_records, get_record


def render_field(field, value=None) -> str:
    field_id = field.id
    field_label = field.label
    field_type = field.type
    required = "required" if field.required else ""
    placeholder = field.placeholder or f"{field_label}..."
    
    required_star = '<span class="text-danger ms-1">*</span>' if field.required else ""
    
    if field_type == "hidden":
        return f'<input type="hidden" id="{field_id}" name="{field_id}" value="{value or ""}">'
    
    if field_type == "text":
        return f'''
        <div class="mb-3">
            <label class="form-label fw-semibold" for="{field_id}">{field_label}{required_star}</label>
            <input type="text" class="form-control form-control-lg {required}" id="{field_id}" name="{field_id}" 
                   placeholder="{placeholder}" value="{value or ""}">
        </div>
        '''
    
    if field_type == "email":
        return f'''
        <div class="mb-3">
            <label class="form-label fw-semibold" for="{field_id}">{field_label}{required_star}</label>
            <input type="email" class="form-control form-control-lg {required}" id="{field_id}" name="{field_id}" 
                   placeholder="{placeholder}" value="{value or ""}">
        </div>
        '''
    
    if field_type == "password":
        return f'''
        <div class="mb-3">
            <label class="form-label fw-semibold" for="{field_id}">{field_label}{required_star}</label>
            <input type="password" class="form-control form-control-lg {required}" id="{field_id}" name="{field_id}" 
                   placeholder="{placeholder}">
        </div>
        '''
    
    if field_type == "number":
        return f'''
        <div class="mb-3">
            <label class="form-label fw-semibold" for="{field_id}">{field_label}{required_star}</label>
            <input type="number" class="form-control form-control-lg {required}" id="{field_id}" name="{field_id}" 
                   placeholder="0" value="{value or ""}">
        </div>
        '''
    
    if field_type == "date":
        return f'''
        <div class="mb-3">
            <label class="form-label fw-semibold" for="{field_id}">{field_label}{required_star}</label>
            <input type="date" class="form-control form-control-lg {required}" id="{field_id}" name="{field_id}" 
                   value="{value or ""}">
        </div>
        '''
    
    if field_type == "textarea":
        return f'''
        <div class="mb-3">
            <label class="form-label fw-semibold" for="{field_id}">{field_label}{required_star}</label>
            <textarea class="form-control form-control-lg {required}" id="{field_id}" name="{field_id}" 
                      rows="4" placeholder="{placeholder}">{value or ""}</textarea>
        </div>
        '''
    
    if field_type == "select":
        options_html = ""
        for opt in field.options:
            selected = "selected" if str(value) == str(opt.get("value", "")) else ""
            options_html += f'<option value="{opt.get("value", "")}" {selected}>{opt.get("label", "")}</option>'
        
        return f'''
        <div class="mb-3">
            <label class="form-label fw-semibold" for="{field_id}">{field_label}{required_star}</label>
            <select class="form-select form-select-lg {required}" id="{field_id}" name="{field_id}">
                {options_html}
            </select>
        </div>
        '''
    
    if field_type == "radio":
        radios_html = ""
        for opt in field.options:
            checked = "checked" if str(value) == str(opt.get("value", "")) else ""
            opt_id = f"{field_id}_{opt.get('value', '')}"
            radios_html += f'''
            <div class="form-check form-check-inline me-4">
                <input class="form-check-input" type="radio" id="{opt_id}" name="{field_id}" 
                       value="{opt.get("value", "")}" {checked}>
                <label class="form-check-label fw-medium ms-2" for="{opt_id}">{opt.get("label", "")}</label>
            </div>
            '''
        
        return f'''
        <div class="mb-3">
            <label class="form-label fw-semibold d-block">{field_label}</label>
            <div class="mt-2">{radios_html}</div>
        </div>
        '''
    
    if field_type == "checkbox":
        checked = "checked" if value else ""
        return f'''
        <div class="mb-3 form-check">
            <input class="form-check-input" type="checkbox" id="{field_id}" name="{field_id}" value="T" {checked}>
            <label class="form-check-label fw-semibold" for="{field_id}">{field_label}</label>
        </div>
        '''
    
    if field_type == "file":
        preview = ""
        if value:
            cache_buster = random.randint(1, 10000)
            preview = f'''
            <div class="mb-2">
                <img src="/uploads/{value}?v={cache_buster}" 
                     alt="{value}" style="max-width: 100%; height: auto;">
                <div class="text-muted small mt-1">{value}</div>
            </div>
            '''
        
        return f'''
        <div class="mb-3">
            <label class="form-label fw-semibold" for="{field_id}">{field_label}{required_star}</label>
            {preview}
            <input type="file" class="form-control form-control-lg" id="{field_id}" name="{field_id}" accept="image/*">
        </div>
        '''
    
    return f'''
    <div class="mb-3">
        <label class="form-label fw-semibold" for="{field_id}">{field_label}{required_star}</label>
        <input type="text" class="form-control form-control-lg {required}" id="{field_id}" name="{field_id}" 
               placeholder="{placeholder}" value="{value or ""}">
    </div>
    '''


def render_form(entity: str, row: Optional[dict] = None, csrf_token: str = "", parent_entity: str = "", parent_id: Optional[int] = None) -> str:
    cfg = EntityConfigManager.get(entity)
    if not cfg:
        return "<div class='alert alert-danger'>Entity not found</div>"
    
    fields = cfg.get_form_fields()
    fields_html = ""
    
    for field in fields:
        value = row.get(field.id) if row else None
        fields_html += render_field(field, value)
    
    redirect_hidden = ""
    if parent_entity and parent_id:
        redirect_hidden = f'<input type="hidden" name="_redirect_url" value="/admin/{parent_entity}?id={parent_id}&tab={entity}">'
    
    return f'''
    <form method="POST" action="/admin/{entity}/save" enctype="multipart/form-data" class="needs-validation" novalidate>
        <input type="hidden" name="csrf_token" value="{csrf_token}">
        {redirect_hidden}
        {fields_html}
        <div class="d-flex gap-2 justify-content-end mt-4">
            <button type="submit" class="btn btn-primary btn-lg fw-semibold shadow-sm rounded">
                <i class="bi bi-check-lg me-2"></i>Submit
            </button>
            <button type="button" class="btn btn-outline-secondary btn-lg fw-semibold shadow-sm rounded cancel-btn" data-bs-dismiss="modal">
                <i class="bi bi-x-lg me-2"></i>Cancel
            </button>
        </div>
    </form>
    '''


def render_subgrid_table(entity: str, parent_entity: str, subgrid, selected_id: Optional[int]) -> str:
    """Render a subgrid placeholder that will be loaded via AJAX."""
    sg_name = subgrid.entity.replace("_", "-").lower()
    table_id = f"{parent_entity}-{sg_name}-table"
    
    return f'''
    <div class="subgrid-loading text-center p-4">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-2">Loading...</p>
    </div>
    <div class="subgrid-table-wrapper" style="display:none">
        <table id="{table_id}" class="table table-hover table-bordered table-sm w-100">
            <thead><tr></tr></thead>
            <tbody></tbody>
        </table>
    </div>
    '''


def render_parent_detail_vertical(entity: str, row: Optional[dict], actions: dict) -> str:
    """Render parent record as vertical detail view (field-value pairs in rows)."""
    cfg = EntityConfigManager.get(entity)
    if not cfg:
        return "<div class='alert alert-danger'>Entity not found</div>"
    
    if not row:
        return '''
        <div class="text-center p-4">
            <i class="bi bi-inbox text-muted" style="font-size: 3rem;"></i>
            <p class="text-muted mt-2">No record selected</p>
        </div>
        '''
    
    fields = cfg.get_display_fields()
    rows_html = ""
    
    for field in fields:
        value = row.get(field.id, "")
        field_label = field.label
        
        if field.type == "file" and value:
            display_value = f'<img src="/uploads/{value}" alt="{value}" style="max-width:100px;max-height:100px;border-radius:8px;">'
        elif field.type == "file":
            display_value = '<span class="text-muted">-</span>'
        elif field.type == "select" or field.type == "radio":
            # Look up label from options
            display_value = "-"
            if value:
                for opt in field.options:
                    if str(opt.get("value", "")) == str(value):
                        display_value = opt.get("label", value)
                        break
                else:
                    display_value = value
        else:
            display_value = value or "-"
        
        rows_html += f'''
        <tr>
            <th class="bg-light text-uppercase fw-semibold" style="width:30%;">{field_label}</th>
            <td>{display_value}</td>
        </tr>
        '''
    
    row_id = row.get("id", "")
    actions_html = ""
    
    if actions.get("edit"):
        edit_url = f"/admin/{entity}/edit-form/{row_id}"
        actions_html += f'<a href="#" class="btn btn-warning btn-sm edit-record-btn" data-url="{edit_url}"><i class="bi bi-pencil me-1"></i>Edit</a>'
    
    if actions.get("delete"):
        delete_url = f"/admin/{entity}/delete/{row_id}"
        actions_html += f'<a href="{delete_url}" class="btn btn-danger btn-sm delete-record-btn"><i class="bi bi-trash me-1"></i>Delete</a>'
    
    rows_html += f'''
    <tr>
        <th class="bg-light text-uppercase fw-semibold">Actions</th>
        <td><div class="btn-group btn-group-sm">{actions_html}</div></td>
    </tr>
    '''
    
    return f'''
    <div class="parent-record-view">
        <table class="table table-bordered table-hover mb-0">
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    '''


def render_parent_selector_modal(entity: str, all_rows: list, fields: list) -> str:
    """Render modal for selecting a parent record with DataTables."""
    cfg = EntityConfigManager.get(entity)
    modal_id = f"{entity}-select-parent-modal"
    table_id = f"{entity}-select-table"
    
    thead_cells = '<th style="width:80px;">Select</th>'
    for field in fields:
        thead_cells += f'<th>{field.label}</th>'
    
    tbody_rows = ""
    for row in all_rows:
        cells = f'<td><button class="btn btn-success btn-sm select-parent-btn" data-parent-id="{row.get("id")}"><i class="bi bi-check-circle me-1"></i>Select</button></td>'
        for field in fields:
            value = row.get(field.id, "-") or "-"
            cells += f'<td>{value}</td>'
        tbody_rows += f'<tr>{cells}</tr>'
    
    return f'''
    <div class="modal fade" id="{modal_id}" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title"><i class="bi bi-search me-2"></i>Select {cfg.title}</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-0">
                    <table id="{table_id}" class="table table-hover table-striped table-sm w-100">
                        <thead class="table-light">
                            <tr>{thead_cells}</tr>
                        </thead>
                        <tbody>{tbody_rows}</tbody>
                    </table>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>
    '''


def render_tabgrid_js(entity: str, selected_id: Optional[int], has_subgrids: bool) -> str:
    """Render JavaScript for TabGrid functionality."""
    modal_id = f"{entity}-select-parent-modal"
    table_id = f"{entity}-select-table"
    selected_id_str = str(selected_id) if selected_id else ""
    
    subgrid_js = ""
    if has_subgrids:
        subgrid_js = '''
        // Define loadSubgridData function FIRST
        window.loadSubgridData = function(pane) {
            const subgridEntity = pane.dataset.subgridEntity;
            const foreignKey = pane.dataset.foreignKey;
            const parentId = pane.dataset.parentId;
            
            if (!parentId || parentId === '' || parentId === 'None') {
                pane.querySelector('.subgrid-loading').innerHTML = '<div class="alert alert-warning">Please select a parent record first</div>';
                return;
            }
            
            const loadingDiv = pane.querySelector('.subgrid-loading');
            const tableWrapper = pane.querySelector('.subgrid-table-wrapper');
            
            $.ajax({
                url: '/admin/subgrid',
                method: 'GET',
                data: {
                    entity: subgridEntity,
                    parent_id: parentId,
                    foreign_key: foreignKey
                },
                success: function(response) {
                    if (loadingDiv) loadingDiv.style.display = 'none';
                    if (tableWrapper) tableWrapper.style.display = 'block';
                    
                    const tableId = tableWrapper.querySelector('table').id;
                    window.renderSubgridTable(tableId, response.rows, response.fields, response.field_types, response.field_options, subgridEntity, parentId);
                    pane.dataset.loaded = 'true';
                },
                error: function(xhr, status, error) {
                    console.error('loadSubgridData error:', error);
                    if (loadingDiv) {
                        loadingDiv.innerHTML = '<div class="alert alert-danger">Failed to load subgrid data: ' + error + '</div>';
                    }
                }
            });
        };
        
        window.renderSubgridTable = function(tableId, rows, fields, fieldTypes, fieldOptions, subgridEntity, parentId) {
            const table = $('#' + tableId);
            
            if ($.fn.DataTable.isDataTable(table)) {
                table.DataTable().destroy();
            }
            
            // Build thead
            let theadHtml = '<tr>';
            for (const [fieldId, fieldLabel] of Object.entries(fields)) {
                theadHtml += '<th>' + fieldLabel + '</th>';
            }
            theadHtml += '<th>Actions</th></tr>';
            table.find('thead').html(theadHtml);
            
            const columns = [];
            for (const [fieldId, fieldLabel] of Object.entries(fields)) {
                const fieldType = fieldTypes[fieldId];
                const options = fieldOptions[fieldId] || {};
                
                columns.push({ 
                    data: fieldId,
                    render: function(data, type, row) {
                        if (type === 'display') {
                            if (fieldType === 'file' || fieldId === 'imagen' || fieldId === 'image') {
                                if (data) {
                                    return '<img src="/uploads/' + data + '" style="max-width:50px;max-height:50px;border-radius:4px;">';
                                }
                                return '-';
                            }
                            if (fieldType === 'select' || fieldType === 'radio') {
                                if (data && options[String(data)]) {
                                    return options[String(data)];
                                }
                                return data || '-';
                            }
                            if (data === null || data === undefined) return '-';
                            return data;
                        }
                        return data;
                    }
                });
            }
            columns.push({
                data: null,
                render: function(data, type, row) {
                    const editUrl = '/admin/' + subgridEntity + '/edit-form/' + row.id + '?parent_entity=' + window.tabgridEntity + '&parent_id=' + parentId;
                    const deleteUrl = '/admin/' + subgridEntity + '/delete/' + row.id + '?parent_entity=' + window.tabgridEntity + '&parent_id=' + parentId;
                    return '<div class="btn-group btn-group-sm">' +
                        '<a href="#" class="btn btn-warning btn-sm edit-record-btn" data-url="' + editUrl + '"><i class="bi bi-pencil"></i></a>' +
                        '<a href="' + deleteUrl + '" class="btn btn-danger btn-sm delete-record-btn"><i class="bi bi-trash"></i></a>' +
                        '</div>';
                }
            });
            
            var dtConfig = {
                data: rows,
                columns: columns,
                responsive: true,
                pageLength: 10,
                dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>Brtip',
                buttons: [
                    { extend: 'excel', className: 'btn btn-success btn-sm', text: '<i class="bi bi-file-earmark-excel"></i> Excel' },
                    { extend: 'pdf', className: 'btn btn-danger btn-sm', text: '<i class="bi bi-file-earmark-pdf"></i> PDF' },
                    { extend: 'print', className: 'btn btn-info btn-sm', text: '<i class="bi bi-printer"></i> Print' }
                ]
            };
            if (typeof LOCALE !== 'undefined' && LOCALE !== 'en') {
                var langMap = { 'es': 'es-ES', 'fr': 'fr-FR', 'de': 'de-DE', 'pt': 'pt-PT', 'it': 'it-IT' };
                var langCode = langMap[LOCALE] || LOCALE;
                dtConfig.language = { url: 'https://cdn.datatables.net/plug-ins/1.13.7/i18n/' + langCode + '.json' };
            }
            var dt = table.DataTable(dtConfig);
            dt.buttons().container().appendTo('#' + tableId + '_wrapper .col-md-6:eq(0)');
        };
        
        // Tab switching for subgrids - use Bootstrap's shown.bs.tab event
        $(document).on('shown.bs.tab', '.nav-tabs .nav-link', function (e) {
            const targetId = e.target.dataset.bsTarget || e.target.getAttribute('href');
            const targetPane = document.querySelector(targetId);
            
            if (targetPane && targetPane.dataset.subgridEntity && targetPane.dataset.loaded !== 'true') {
                window.loadSubgridData(targetPane);
            }
        });
        
        // Check for already active tabs on page load (after functions are defined)
        $('.nav-tabs .nav-link.active').each(function() {
            const targetId = this.dataset.bsTarget || this.getAttribute('href');
            const targetPane = document.querySelector(targetId);
            if (targetPane && targetPane.dataset.subgridEntity && targetPane.dataset.loaded !== 'true') {
                window.loadSubgridData(targetPane);
            }
        });
        
        // Add subgrid button handler
        $(document).on('click', '.add-subgrid-btn', function(e) {
            e.preventDefault();
            const subgridEntity = $(this).data('subgrid-entity');
            const parentId = $(this).data('parent-id');
            const url = '/admin/' + subgridEntity + '/add-form/' + parentId + '?parent_entity=' + window.tabgridEntity;
            
            var modal = $('#exampleModal');
            modal.find('.modal-body').html('<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></div>');
            modal.find('.modal-title').text('New Record');
            modal.modal('show');
            $.get(url, function(html) {
                modal.find('.modal-body').html(html);
            }).fail(function() {
                modal.find('.modal-body').html('<div class="alert alert-danger">Error loading form</div>');
            });
        });
        '''
    
    return f'''
    <script>
    // Wait for jQuery to be loaded
    (function() {{
        function initTabgrid() {{
            window.tabgridEntity = '{entity}';
            window.tabgridSelectedId = '{selected_id_str}';
            
            // Initialize DataTable on parent selector modal
            const table = $('#{table_id}');
            if (table.length && !$.fn.DataTable.isDataTable(table)) {{
                var dtConfig = {{
                    responsive: true,
                    pageLength: 10,
                    order: [[1, 'asc']],
                    dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>Brtip',
                    buttons: [
                        {{ extend: 'excel', className: 'btn btn-success btn-sm', text: '<i class="bi bi-file-earmark-excel"></i> Excel' }},
                        {{ extend: 'pdf', className: 'btn btn-danger btn-sm', text: '<i class="bi bi-file-earmark-pdf"></i> PDF' }},
                        {{ extend: 'print', className: 'btn btn-info btn-sm', text: '<i class="bi bi-printer"></i> Print' }}
                    ]
                }};
                if (typeof LOCALE !== 'undefined' && LOCALE !== 'en') {{
                    var langMap = {{ 'es': 'es-ES', 'fr': 'fr-FR', 'de': 'de-DE', 'pt': 'pt-PT', 'it': 'it-IT' }};
                    var langCode = langMap[LOCALE] || LOCALE;
                    dtConfig.language = {{ url: 'https://cdn.datatables.net/plug-ins/1.13.7/i18n/' + langCode + '.json' }};
                }}
                var dt = table.DataTable(dtConfig);
                dt.buttons().container().appendTo('#{table_id}_wrapper .col-md-6:eq(0)');
            }}
            
            // Select parent button handler
            $(document).on('click', '.select-parent-btn', function(e) {{
                e.preventDefault();
                e.stopPropagation();
                const parentId = $(this).data('parent-id');
                $('#{modal_id}').modal('hide');
                window.location.href = '/admin/{entity}?id=' + parentId;
            }});
            
            {subgrid_js}
            
            // Check for tab parameter in URL and auto-select that tab
            const urlParams = new URLSearchParams(window.location.search);
            const tabParam = urlParams.get('tab');
            if (tabParam) {{
                const tabLink = document.querySelector('[href="#tab-' + tabParam + '"]');
                const targetPane = document.querySelector('#tab-' + tabParam);
                if (tabLink && targetPane) {{
                    // Show the tab
                    $(tabLink).tab('show');
                    // Manually load subgrid data if needed
                    if (targetPane.dataset.subgridEntity && targetPane.dataset.loaded !== 'true') {{
                        setTimeout(function() {{
                            window.loadSubgridData(targetPane);
                        }}, 100);
                    }}
                }}
            }}
        }}
        
        // Run when jQuery is ready
        if (typeof $ === 'function') {{
            $(initTabgrid);
        }} else {{
            document.addEventListener('DOMContentLoaded', function() {{
                if (typeof $ === 'function') {{
                    $(initTabgrid);
                }} else {{
                    console.error('jQuery not loaded');
                }}
            }});
        }}
    }})();
    </script>
    '''


def render_tabbed_view(entity: str, selected_id: Optional[int] = None, current_tab: str = "") -> str:
    """
    Render tabbed view for ALL entities (matches Clojure tabgrid).
    
    - All grids use tabbed interface (even without subgrids)
    - First record shown by default if no selected_id
    - Select + New button in header
    - Vertical parent detail view
    - Subgrids with DataTables for filter/sort
    """
    cfg = EntityConfigManager.get(entity)
    if not cfg:
        return "<div class='alert alert-danger'>Entity not found</div>"
    
    all_rows = list_records(entity)
    actions = cfg.actions
    has_subgrids = bool(cfg.subgrids)
    
    first_row = all_rows[0] if all_rows else None
    
    if not selected_id and first_row:
        selected_id = first_row.get("id")
    
    selected_row = get_record(entity, selected_id) if selected_id else None
    
    fields = cfg.get_display_fields()
    
    modal_id = f"{entity}-select-parent-modal"
    
    header_new_button = ""
    if actions.get("new"):
        new_url = f"/admin/{entity}/add-form"
        header_new_button = f'''
        <a href="{new_url}" class="btn btn-success new-record-btn" data-url="{new_url}">
            <i class="bi bi-plus-circle me-1"></i>New
        </a>
        '''
    
    header = f'''
    <div class="card shadow-sm mb-3">
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h3 class="mb-0">
                        <i class="bi bi-layers me-2"></i>{cfg.title}
                        <span class="badge bg-secondary ms-2">{len(all_rows)} items</span>
                    </h3>
                </div>
                <div class="btn-group">
                    <button type="button" class="btn btn-outline-primary" data-bs-toggle="modal" data-bs-target="#{modal_id}">
                        <i class="bi bi-search me-1"></i>Select
                    </button>
                    {header_new_button}
                    <button type="button" class="btn btn-outline-secondary" onclick="location.reload()">
                        <i class="bi bi-arrow-clockwise me-1"></i>Refresh
                    </button>
                </div>
            </div>
        </div>
    </div>
    '''
    
    selector_modal = render_parent_selector_modal(entity, all_rows, fields) if all_rows else ""
    
    if not has_subgrids:
        parent_detail = render_parent_detail_vertical(entity, selected_row, actions)
        js = render_tabgrid_js(entity, selected_id, False)
        return f'''
        <div class="tabgrid-container" data-entity="{entity}" data-selected-parent-id="{selected_id or ""}">
            {header}
            {selector_modal}
            <div class="card shadow-sm">
                <div class="card-body">
                    {parent_detail}
                </div>
            </div>
            {js}
        </div>
        '''
    
    tabs_nav = ""
    tabs_content = ""
    
    main_active = "active" if not current_tab or current_tab == entity else ""
    tabs_nav += f'<li class="nav-item"><a class="nav-link {main_active}" data-bs-toggle="tab" href="#tab-{entity}"><i class="bi bi-table me-2"></i>{cfg.title}</a></li>'
    
    parent_detail = render_parent_detail_vertical(entity, selected_row, actions)
    tabs_content += f'''
    <div class="tab-pane fade show {main_active}" id="tab-{entity}">
        <div class="card shadow-sm">
            <div class="card-body">
                {parent_detail}
            </div>
        </div>
    </div>
    '''
    
    for i, subgrid in enumerate(cfg.subgrids):
        sub_active = "active" if current_tab == subgrid.entity else ""
        sub_show = "show" if current_tab == subgrid.entity else ""
        tabs_nav += f'<li class="nav-item"><a class="nav-link {sub_active}" data-bs-toggle="tab" href="#tab-{subgrid.entity}"><i class="{subgrid.icon} me-2"></i>{subgrid.title}</a></li>'
        
        sub_table = render_subgrid_table(subgrid.entity, entity, subgrid, selected_id)
        add_button = f'''
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="mb-0"><i class="{subgrid.icon} me-2"></i>{subgrid.title}</h5>
            <button class="btn btn-sm btn-primary add-subgrid-btn" data-subgrid-entity="{subgrid.entity}" data-parent-id="{selected_id or ""}">
                <i class="bi bi-plus-circle me-1"></i>New
            </button>
        </div>
        '''
        
        tabs_content += f'''
        <div class="tab-pane fade {sub_show} {sub_active}" id="tab-{subgrid.entity}" data-subgrid-entity="{subgrid.entity}" data-foreign-key="{subgrid.foreign_key}" data-parent-id="{selected_id or ""}" data-loaded="false">
            <div class="card shadow-sm">
                <div class="card-body">
                    {add_button}
                    {sub_table}
                </div>
            </div>
        </div>
        '''
    
    js = render_tabgrid_js(entity, selected_id, True)
    
    return f'''
    <div class="tabgrid-container" data-entity="{entity}" data-selected-parent-id="{selected_id or ""}">
        {header}
        {selector_modal}
        <ul class="nav nav-tabs mb-3">{tabs_nav}</ul>
        <div class="tab-content">{tabs_content}</div>
        {js}
    </div>
    '''


def render_grid(entity: str, rows: list, parent_id: Optional[int] = None, parent_entity: str = "") -> str:
    """
    Render a standard grid (used for standalone views without tabbed interface).
    For tabbed views, use render_tabbed_view instead.
    """
    cfg = EntityConfigManager.get(entity)
    if not cfg:
        return "<div class='alert alert-danger'>Entity not found</div>"
    
    fields = cfg.get_display_fields()
    actions = cfg.actions
    
    thead_cells = ""
    for field in fields:
        thead_cells += f'<th class="text-nowrap text-uppercase fw-semibold">{field.label}</th>'
    
    thead_cells += '<th class="text-center" style="width:1%; white-space:nowrap;">Actions</th>'
    
    tbody_rows = ""
    if not rows:
        tbody_rows = f'<tr><td colspan="{len(fields) + 1}" class="text-center text-muted"><em>No records found</em></td></tr>'
    else:
        for row in rows:
            cells = ""
            for field in fields:
                value = row.get(field.id, "")
                if field.type == "file" and value:
                    cells += f'<td class="align-middle"><img src="/uploads/{value}" alt="{value}" style="max-width:60px;max-height:60px;border-radius:8px;object-fit:cover;"></td>'
                elif field.type == "file":
                    cells += '<td class="align-middle text-muted">-</td>'
                else:
                    cells += f'<td class="text-truncate align-middle">{value or "-"}</td>'
            
            row_id = row.get("id", "")
            actions_html = ""
            
            if actions.get("edit"):
                edit_url = f"/admin/{entity}/edit-form/{row_id}?parent_entity={parent_entity}&parent_id={parent_id}" if parent_entity and parent_id else f"/admin/{entity}/edit-form/{row_id}"
                actions_html += f'<a href="#" class="btn btn-warning btn-sm edit-record-btn" data-url="{edit_url}"><i class="bi bi-pencil"></i></a>'
            
            if actions.get("delete"):
                delete_url = f"/admin/{entity}/delete/{row_id}?parent_entity={parent_entity}&parent_id={parent_id}" if parent_entity and parent_id else f"/admin/{entity}/delete/{row_id}"
                actions_html += f'<a href="{delete_url}" class="btn btn-danger btn-sm delete-record-btn" data-entity="{entity}" data-id="{row_id}"><i class="bi bi-trash"></i></a>'
            
            cells += f'<td class="text-center align-middle"><div class="d-flex justify-content-center gap-1">{actions_html}</div></td>'
            tbody_rows += f'<tr>{cells}</tr>'
    
    new_url = f"/admin/{entity}/add-form/{parent_id}?parent_entity={parent_entity}" if parent_id and parent_entity else f"/admin/{entity}/add-form"
    
    new_button = ""
    if actions.get("new"):
        new_button = f'<a href="#" class="btn btn-success new-record-btn" data-url="{new_url}"><i class="bi bi-plus-lg me-1"></i>New</a>'
    
    return f'''
    <div class="card shadow mb-4">
        <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0"><i class="bi bi-table me-2"></i>{cfg.title}</h5>
            {new_button}
        </div>
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover table-bordered table-striped table-sm align-middle mb-0">
                    <thead class="table-light">{thead_cells}</thead>
                    <tbody>{tbody_rows}</tbody>
                </table>
            </div>
        </div>
    </div>
    '''


def render_error(message: str) -> str:
    return f'<div class="alert alert-danger m-3"><i class="bi bi-exclamation-triangle me-2"></i>{message}</div>'


def build_dashboard(title: str, rows: list, table_id: str, fields: dict) -> tuple:
    """
    Build a dashboard/report DataTable with export buttons.
    
    Args:
        title: The title/heading for the dashboard
        rows: List of dictionaries with data
        table_id: Unique ID for the table element
        fields: Dict mapping field names to labels, e.g. {"name": "Name", "email": "Email"}
    
    Returns:
        Tuple of (html, javascript) strings
    """
    thead_cells = "".join(f'<th class="text-nowrap text-uppercase fw-semibold">{label}</th>' for label in fields.values())
    
    tbody_rows = ""
    for row in rows:
        tbody_rows += "<tr>"
        for field_name in fields.keys():
            value = row.get(field_name, "")
            tbody_rows += f'<td class="text-truncate align-middle">{value}</td>'
        tbody_rows += "</tr>"
    
    html = f'''
    <div class="card shadow mb-4">
        <div class="card-body bg-gradient bg-primary text-white rounded-top">
            <h4 class="mb-0 fw-bold">{title}</h4>
        </div>
        <div class="p-3 bg-white rounded-bottom">
            <div class="table-responsive">
                <table id="{table_id}" class="table table-hover table-bordered table-striped table-sm align-middle display dataTable w-100">
                    <thead class="table-light">
                        <tr>{thead_cells}</tr>
                    </thead>
                    <tbody>{tbody_rows}</tbody>
                </table>
            </div>
        </div>
    </div>
    '''
    
    javascript = f'''
    <script>
    $(function() {{
        var dtConfig = {{
            responsive: true,
            pageLength: 25,
            order: [[0, 'asc']],
            dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>Brtip',
            buttons: [
                {{ extend: 'excel', className: 'btn btn-success btn-sm', text: '<i class="bi bi-file-earmark-excel"></i> Excel' }},
                {{ extend: 'pdf', className: 'btn btn-danger btn-sm', text: '<i class="bi bi-file-earmark-pdf"></i> PDF' }},
                {{ extend: 'print', className: 'btn btn-info btn-sm', text: '<i class="bi bi-printer"></i> Print' }}
            ]
        }};
        if (typeof LOCALE !== 'undefined' && LOCALE !== 'en') {{
            var langMap = {{ 'es': 'es-ES', 'fr': 'fr-FR', 'de': 'de-DE', 'pt': 'pt-PT', 'it': 'it-IT' }};
            var langCode = langMap[LOCALE] || LOCALE;
            dtConfig.language = {{ url: 'https://cdn.datatables.net/plug-ins/1.13.7/i18n/' + langCode + '.json' }};
        }}
        var dt = $('#{table_id}').DataTable(dtConfig);
        dt.buttons().container().appendTo('#{table_id}_wrapper .col-md-6:eq(0)');
    }});
    </script>
    '''
    
    return html, javascript
