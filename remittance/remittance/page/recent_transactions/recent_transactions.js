frappe.pages['recent-transactions'].on_page_load = function(wrapper) {
	new PageContent(wrapper);
}

PageContent = Class.extend({

    init: function(wrapper) {
        this.wrapper = wrapper;
        this.transactions = [];
        this.current_page = 1;
        this.has_more = false;
        this.page = frappe.ui.make_app_page({
            parent: wrapper,
            title: __('Recent Transactions'),
            single_column: true
        });

        this.make();
		// this.page.add_inner_button(__("Send Money"), function() {
        //     frappe.new_doc('Transaction');
        // }).addClass('btn btn-primary');
    },

    make: function() {
        const htmlContent = `
			<div class="layout-main-section-wrapper">
				<div class="layout-main-section layout-main-list">
					<div class="page-form flex">
						<div class="standard-filter-section flex">
							<div
								class="form-group frappe-control  col-md-3"

							>
								<input
									type="text"
									autocomplete="off"
									class="input-with-feedback form-control input-xs search-input"
									maxlength="140"
									data-fieldtype="Data"
									data-fieldname="name"
									placeholder="Search by Transaction ID..."
								/><span class="tooltip-content">name</span>
							</div>

						</div>

					</div>
					<div class="frappe-list">
						<div class="result" style="height:80vh">
							<div class="list-row-container">
								<header class="level list-row-head text-muted">
									<div class="level-left list-header-subject">
										<div class="list-row-col ellipsis list-subject level ml-2">

											Transaction ID
										</div>
										<div class="list-row-col ellipsis list-subject level ">

											Receiver ID
										</div>
										<div class="list-row-col ellipsis list-subject level ">

											Mobile Number
										</div>
										<div class="list-row-col ellipsis list-subject level ">
											Receiver Name

										</div>
										<div class="list-row-col ellipsis list-subject level ">
											Sender Name

										</div>
										<div class="list-row-col ellipsis list-subject level ">
											Currency

										</div>
										<div class="list-row-col ellipsis list-subject level ">
											Amount

										</div>
										<div class="list-row-col ellipsis list-subject level ">
											Status

										</div>

										<div class="list-row-col ellipsis list-subject level ">
											Action

										</div>
									</div>

								</header>
							</div>
							<div id="transaction-table-body"></div>
						</div>
					</div>

				</div>
			</div>
            `;

        $(htmlContent).appendTo(this.page.main);
        this.bind_events();
        this.load_data();
    },

    bind_events: function() {
        const self = this;
        let timeout;

        $(this.page.main).on('input', '.search-input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                this.current_page = 1;
                this.load_data();
            }, 500);
        });
    },

    load_data: function() {
		const search_text = $(this.page.main).find('.search-input').val().trim();

		frappe.call({
			method: 'remittance.remittance.page.recent_transactions.recent_transactions.get_recent_trans',
			args: {
				search_text: search_text
			},
			// freeze: true,
			callback: (r) => {
				if (!r.exc) {
					this.transactions = r.message || [];
					this.render_transactions();
				}
			}
		});
	},


    render_transactions: function() {
        const tbody = $(this.page.main).find('#transaction-table-body');
        tbody.empty();

        if (!this.transactions.length) {
            tbody.append(`

				<div
					class="freeze flex justify-center align-center text-muted mt-4"

				>
					 ${__('No transactions found')}
				</div>
            `);
            return;
        }

        this.transactions.forEach(transaction => {
            const modified_date = transaction.modified
                ? frappe.datetime.str_to_user(transaction.modified.split('.')[0])
                : '';

            const row = `
				<div class="list-row-container" tabindex="1">
					<div class="level list-row">
						<div class="level-left ellipsis ml-2 ">

							<div class="list-row-col ellipsis hidden-xs">
								<span class="ellipsis" title="ID: TC000002">
									<a class="filterable ellipsis" data-filter="name,=,TC000002">
										${transaction.name || ''}
									</a>
								</span>
							</div>
							<div class="list-row-col ellipsis hidden-xs">
								<span class="ellipsis" title="ID: TC000002">
									<a class="filterable ellipsis" data-filter="name,=,TC000002">
										${transaction.receiver_id || ''}
									</a>
								</span>
							</div>
							<div class="list-row-col ellipsis hidden-xs">
								<span class="ellipsis" title="ID: TC000002">
									<a class="filterable ellipsis" data-filter="name,=,TC000002">
										${transaction.mobile_no || ''}
									</a>
								</span>
							</div>
							<div class="list-row-col ellipsis hidden-xs">
								<span class="ellipsis" title="ID: TC000002">
									<a class="filterable ellipsis" data-filter="name,=,TC000002">
										${transaction.receiver_name || ''}
									</a>
								</span>
							</div>
							<div class="list-row-col ellipsis hidden-xs">
								<span class="ellipsis" title="ID: TC000002">
									<a class="filterable ellipsis" data-filter="name,=,TC000002">
										${transaction.sender_name || ''}
									</a>
								</span>
							</div>
							<div class="list-row-col ellipsis hidden-xs">
								<span class="ellipsis" title="ID: TC000002">
									<a class="filterable ellipsis" data-filter="name,=,TC000002">
										${transaction.currency || ''}
									</a>
								</span>
							</div>
							<div class="list-row-col ellipsis hidden-xs">
								<span class="ellipsis" title="ID: TC000002">
									<a class="filterable ellipsis" data-filter="name,=,TC000002">
										${parseFloat(transaction.receiver_amount).toFixed(2) || '0.00'}
									</a>
								</span>
							</div>
							<div class="list-row-col ellipsis hidden-xs"
								>
								<span class="ellipsis" title="Transaction Status: ${transaction.transaction_status || ''}">
									<span class="filterable indicator-pill ${transaction.transaction_status === 'Completed' ? 'green' : transaction.transaction_status === 'Pending' ? 'yellow' : transaction.transaction_status === 'Rejected' ? 'red' : 'red'} ellipsis"
										data-filter="transaction_status,=,${transaction.transaction_status || ''}">
										<span class="ellipsis">${transaction.transaction_status || 'Unknown'}</span>
									</span>
								</span>
							</div>
							<div class="list-row-col ellipsis hidden-xs">
								<span class="ellipsis" title="ID: TC000002">
									<button class="btn btn-xs btn-info view-details"
											data-name="${transaction.name || ''}">
										${__('View')}
									</button>
								</span>
							</div>
						</div>

					</div>
				</div>
              `;

            tbody.append(row);
        });

        $(this.page.main).on('click', '.view-details', (e) => {
            const name = $(e.currentTarget).data('name');
            if (name) {
                frappe.set_route('Form', 'Transaction', name);
            }
        });
    },
});
