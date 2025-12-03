frappe.pages['my-page'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Dashboard',
		single_column: true
	});
	frappe.breadcrumbs.add("Remittance", "Dashboard");
	page.main.html(`
		<main>
			<div class="container-xl p-5">
				<!-- Auto-refresh indicator -->
				<div class="row mb-3">
					<div class="col-12">
						<div class="d-flex justify-content-between align-items-center">
							<div>
								<span class="badge badge-light" id="last-updated">Last updated: Never</span>
								<span class="badge badge-success ms-2" id="auto-refresh-status" style="cursor: pointer;">Auto-refresh: ON</span>
							</div>
							<button class="btn btn-sm btn-outline-primary" id="manual-refresh-btn">
								<i class="fa fa-refresh"></i> Refresh Now
							</button>
						</div>
					</div>
				</div>

				<div class="row gx-5">
					<div class="col-md-4 mb-2">
						<div class="tf-card tf-card-raised tf-border-start tf-border-primary tf-border-4">
						<div class="card-body px-4">
							<div class="d-flex justify-content-between align-items-center mb-2">
								<div class="me-2">
									<div class="display-5" id="float-balance">$0.00</div>
									<div class="card-text">Cash In Hand</div>
								</div>
								<div class="tf-icon-circle tf-bg-primary tf-text-white">
								<span class="sidebar-item-icon" item-icon="accounting">
									<svg class="icon tf-icon icon-md" style="" aria-hidden="true">
										<use class="" href="#icon-accounting"></use>
									</svg>
								</span>
								</div>
							</div>
						</div>
						</div>
					</div>
					<div class="col-md-4 mb-2">
						<div class="tf-card tf-card-raised tf-border-start tf-border-warning tf-border-4">
						<div class="card-body px-4">
							<div class="d-flex justify-content-between align-items-center mb-2">
								<div class="me-2">
									<div class="display-5" id="total-received">$0.00</div>
									<div class="card-text">Total Cash In</div>
								</div>
								<div class="tf-icon-circle tf-bg-warning tf-text-white">
								<span class="sidebar-item-icon" item-icon="accounting">
									<svg class="icon tf-icon icon-md" style="" aria-hidden="true">
										<use class="" href="#icon-accounting"></use>
									</svg>
								</span>
								</div>
							</div>
						</div>
						</div>
					</div>
					<div class="col-md-4 mb-2">
						<div class="tf-card tf-card-raised tf-border-start tf-border-secondary tf-border-4">
						<div class="card-body px-4">
							<div class="d-flex justify-content-between align-items-center mb-2">
								<div class="me-2">
									<div class="display-5" id="total-sent">$0.00</div>
									<div class="card-text">Total Cash Out</div>
								</div>
								<div class="tf-icon-circle tf-bg-secondary tf-text-white">
								<span class="sidebar-item-icon" item-icon="accounting">
									<svg class="icon tf-icon icon-md" style="" aria-hidden="true">
										<use class="" href="#icon-accounting"></use>
									</svg>
								</span>
								</div>
							</div>
						</div>
						</div>
					</div>
					<div class="col-md-4 mb-2" id="active-till-tfa" style="display: none;">
						<a href="/app/till?enabled=1">
						<div class="tf-card tf-card-raised tf-border-start tf-border-secondary tf-border-4">
							<div class="card-body px-4">
								<div class="d-flex justify-content-between align-items-center mb-2">
									<div class="me-2">
										<div class="display-5" id="total-active-till">0</div>
										<div class="card-text">Active Tills</div>
									</div>
									<div class="tf-icon-circle tf-bg-secondary tf-text-white">
										<span class="sidebar-item-icon" item-icon="accounting">
											<svg class="icon tf-icon icon-md" style="" aria-hidden="true">
												<use class="" href="#icon-accounting"></use>
											</svg>
										</span>
									</div>
								</div>
							</div>
						</div>
						</a>
					</div>
				</div>
			</div>
		</main>
	`);

	// Dashboard refresh functionality
	let refreshInterval;
	let isAutoRefreshEnabled = true;
	let lastUpdateTime = null;
	let userHasPermission = false;

	// Check user permissions
	const roles = ['Super Admin', 'Administrator'];
	userHasPermission = roles.some(role => frappe.user.has_role(role));

	// Function to update active tills count
	function updateActiveTillsCount() {
		if (userHasPermission) {
			frappe.db.get_list('Till', {
				filters: {
					enabled: 1
				},
				fields: ['name']
			}).then(active_tills => {
				const active_count = active_tills.length;
				updateValueWithAnimation("total-active-till", active_count);
				document.getElementById("active-till-tfa").style.display = 'block';
			}).catch(error => {
				console.error('Error fetching active tills:', error);
			});
		} else {
			document.getElementById("active-till-tfa").style.display = 'none';
		}
	}

	// Function to update dashboard data
	function updateDashboardData(showAlert = false) {
		// Add loading indicator
		const refreshBtn = document.getElementById("manual-refresh-btn");
		if (refreshBtn) {
			refreshBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Refreshing...';
			refreshBtn.disabled = true;
		}

		// Update balance data
		frappe.call({
			method: "remittance.remittance.page.my_page.my_page.get_balance",
			callback: function(r) {
				if (r.message) {
					// Update values with animation effect
					updateValueWithAnimation("float-balance", r.message.float_balance);
					updateValueWithAnimation("total-received", r.message.total_received);
					updateValueWithAnimation("total-sent", r.message.total_sent);
				}
			},
			error: function() {
				console.error('Error fetching balance data');
			}
		});

		// Update active tills count
		updateActiveTillsCount();

		// Update last updated time and reset button
		setTimeout(() => {
			lastUpdateTime = frappe.datetime.now_datetime();
			const lastUpdatedElement = document.getElementById("last-updated");
			if (lastUpdatedElement) {
				lastUpdatedElement.textContent = `Last updated: ${frappe.datetime.str_to_user(lastUpdateTime)}`;
			}
			
			if (showAlert) {
				frappe.show_alert({
					message: 'Dashboard data refreshed successfully',
					indicator: 'green'
				}, 3);
			}

			// Reset refresh button
			if (refreshBtn) {
				refreshBtn.innerHTML = '<i class="fa fa-refresh"></i> Refresh Now';
				refreshBtn.disabled = false;
			}
		}, 1000);
	}

	// Function to update values with smooth animation
	function updateValueWithAnimation(elementId, newValue) {
		const element = document.getElementById(elementId);
		if (element) {
			const currentValue = element.textContent;
			// Only animate if value has changed
			if (currentValue !== newValue.toString()) {
				element.style.transition = 'all 0.3s ease';
				element.style.transform = 'scale(1.05)';
				element.style.color = '#28a745';
				
				setTimeout(() => {
					element.textContent = newValue;
					element.style.transform = 'scale(1)';
					element.style.color = '';
				}, 150);
			} else {
				element.textContent = newValue;
			}
		}
	}

	// Start auto-refresh functionality
	function startAutoRefresh() {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
		
		// Refresh every 30 seconds (adjust as needed)
		refreshInterval = setInterval(() => {
			if (isAutoRefreshEnabled && document.visibilityState === 'visible') {
				updateDashboardData();
			}
		}, 30000);
		
		const statusElement = document.getElementById("auto-refresh-status");
		if (statusElement) {
			statusElement.textContent = "Auto-refresh: ON";
			statusElement.className = "badge badge-success ms-2";
		}
	}

	// Stop auto-refresh
	function stopAutoRefresh() {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
		const statusElement = document.getElementById("auto-refresh-status");
		if (statusElement) {
			statusElement.textContent = "Auto-refresh: OFF";
			statusElement.className = "badge badge-secondary ms-2";
		}
	}

	// Toggle auto-refresh on status click
	$(document).on('click', '#auto-refresh-status', function() {
		isAutoRefreshEnabled = !isAutoRefreshEnabled;
		if (isAutoRefreshEnabled) {
			startAutoRefresh();
			frappe.show_alert({
				message: 'Auto-refresh enabled',
				indicator: 'green'
			}, 2);
		} else {
			stopAutoRefresh();
			frappe.show_alert({
				message: 'Auto-refresh disabled',
				indicator: 'orange'
			}, 2);
		}
	});

	// Manual refresh button
	$(document).on('click', '#manual-refresh-btn', function() {
		updateDashboardData(true);
	});

	// Refresh when window gets focus (user returns to tab)
	$(window).on('focus', function() {
		if (isAutoRefreshEnabled) {
			updateDashboardData();
		}
	});

	// Listen for real-time updates (if you implement server-side events)
	frappe.realtime.on('dashboard_refresh', function(data) {
		console.log('Real-time dashboard refresh triggered:', data);
		updateDashboardData();
		
		frappe.show_alert({
			message: `New ${data.doctype || 'transaction'} detected. Dashboard updated.`,
			indicator: 'blue'
		}, 4);
	});

	// Initial data load
	updateDashboardData();

	// Start auto-refresh
	startAutoRefresh();

	// Clean up interval when page is destroyed
	$(window).on('beforeunload', function() {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});

	// Add a custom button to the page
	page.add_inner_button(__("Cash Out"), function() {
		frappe.set_route("cash-out");
	}).addClass('btn tf-cash-out-btn');

	// Add a custom button to the page
	page.add_inner_button(__("Send Money"), function() {
		frappe.set_route("Form", "Transaction", "new-transaction");
	}).addClass('btn btn-primary');

	page.add_inner_button(__("Request Additional Allocation"), function() {
		frappe.confirm(
			__("Are you sure you want to request additional allocation?"),
			function() {
				// User confirmed
				frappe.call({
					method: 'remittance.remittance.doctype.transaction.transaction.send_alert_min_threshold',
					freeze: true,
					callback: (r) => {
						frappe.msgprint({
							title: __("Request Sent"),
							message: __("Your request for additional allocation has been sent successfully. We will notify you once it is processed."),
							indicator: 'green'
						});
						// Refresh dashboard after request
						setTimeout(() => updateDashboardData(), 2000);
					}
				});
			},
			function() {
				// User canceled
				frappe.show_alert({
					message: __('Your request for additional allocation has been canceled.'),
					indicator: 'red'
				}, 5);
			}
		);
	}).addClass('btn tf-additional-float-btn');

	page.add_inner_button(__("Submit Daily Reconciliation"), async function () {
		frappe.confirm(
			__("Are you sure you want to submit the daily reconciliation?"),
			function () {
				// User confirmed
				frappe.call({
					method: "remittance.remittance.page.my_page.my_page.get_user_till",
					callback: function (r) {
						console.log(r);
						if (!r.message) {
							frappe.msgprint("You are not assigned to any Till. Please contact your administrator.");
							return;
						}

						const till = r.message.select_till;

						frappe.call({
							method: "remittance.remittance.page.my_page.my_page.create_or_open_reconciliation",
							args: {
								till: till
							},
							callback: function (r2) {
								if (r2.message) {
									frappe.set_route("Form", "Till Reconciliation", r2.message.name);
								} else {
									frappe.msgprint("Could not load reconciliation document.");
								}
							}
						});
					}
				});
			},
			function () {
				// User canceled
				frappe.show_alert({
					message: __('Your daily reconciliation submission has been canceled.'),
					indicator: 'red'
				}, 5);
			}
		);
	}).addClass('btn tf-daily-reconciliation-btn');
}