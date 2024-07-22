class Denomination{
	constructor(credit){
		this.credit = credit;
		this.cycle_count = 0;
	}
}


class InputTable{
	constructor(denominations, serial_number){
		this.denominations = denominations;
		this.serial_number = serial_number;
	}
	initialiseCycleSelection(){
		$('#input-table').empty()
		$('#input-table').append(
			[
				$('<thead>').append(
					$('<tr class="table-primary">').append(
						[
							$('<th scope="col">').text("#"),
							$('<th scope="col">').text("serial number"),
							$('<th scope="col">').text("denom"),
							$('<th scope="col">').text("cycles"),
						]
					)
				),
				$('<tbody>').append(
					this.denominations.map((denomination, index) => (
						$(`<tr class="table-success">`).append([
							$('<th scope="row">').text(index + 1),
							$('<th>').text(this.serial_number),
							$('<th>').text(denomination.credit),
							$('<th>').append(
								$('<div class="input-group">').append(
								$('<input>', {
										class: 'form-control',
										type: 'number',
										min: 0,
										value: denomination.cycle_count,
										step: 1,
										}).on('input', function() {
											denomination.cycle_count = parseInt($(this).val()) || 0;
									})
								)
							)
						])
					))
				)
			]
		)
		$('#run-button').append(
				$('<button class="btn btn-primary">').text('run').on("click", () => {
					const resulting_denominations = input_table.denominations.filter(denomination => denomination.cycle_count != 0)
					if (resulting_denominations.length == 0){
						alert('in order to run, please specify a counter > 0 for at least one denomination')
					}
					else{
						const denominations_for_export = resulting_denominations.reduce((dictionary, denomination) => {
							dictionary[denomination.credit] = denomination.cycle_count;
							return dictionary;
						}, {});
						console.table(denominations_for_export)
					fetch("/api/run", {
						method: "POST",
						body: JSON.stringify(denominations_for_export),
						headers: {
							"Content-Type": "application/json"
						}
					})
					.then((response) => response.json())
					.then((json) => {
							if (json === null) {
								console.log(json);
							}
							else if (json.status_code === 403){
								alert(json.detail);
							}
							fetchStatus();
						})
					.catch(error => {
							console.error('error running cycles with denominations', error);
					})
					}
			})
		)
	}
}

class ResultTable{
	constructor(columns, rows){
		this.columns = columns;
		this.rows = rows;
	}
	displayResults(){
		$('#result-table').empty()
		$('#result-table').append(
			[
				$('<thead>').append(
					$('<tr class="table-primary">').append(
						this.columns.map(column =>$('<th scope="col">').text(column))
					)
				),
				$('<tbody>').append(
						Object.values(this.rows).map(row => (
							$(`<tr id=${row.coin_type} class="table-success">`).append(
								Object.entries(row).map(([key, value]) => $('<th>').text(value))
							)
						))
					)
				]
			)
		}
	}

var input_table_data;
var result_table_data;
var denominations;
var input_table;

function handleStopped(){
	$('#stopped').show()
	$('#running').hide()
	fetch('/api/device_info')
		.then(response => {
			if (!response.ok) {
				throw new Error('Network response was not ok');
			}
			return response.json();
		})
		.then(data => {
			input_table_data = data;
			denominations = data.denominations.map(denomination => new Denomination(denomination));
			input_table = new InputTable(denominations, data.serial_number);
			input_table.initialiseCycleSelection()
		})
		.catch(error => {
			console.error('Error fetching device info:', error);
			$('#errors').show().html('<p>An error occurred while fetching device info.</p>');
	});
}

function handleRunning(){
	$('#stopped').hide()
	$('#running').show()
	function fetchResults() {
		fetch('/api/results')
		.then(response => {
			if (!response.ok) {
				throw new Error('Network response was not ok');
			}
			return response.json();
		})
		.then(data => {
			result_table_data = data;
			const columns = Object.keys(Object.values(result_table_data.coin_results)[0]).map(str => str.replace(/_/g, '\n'))
			const rows = Object.values(result_table_data.coin_results)
			result_table = new ResultTable(columns, rows);
			result_table.displayResults()
		})
		.catch(error => {
			console.error('Error fetching results:', error);
			$('#errors').show().html('<p>error fetching results</p>');
		});
	}
	fetchResults()
	setInterval(fetchResults, 3000);
}

function fetchStatus(){
	fetch('/api/status')
		.then(response => {
			if (!response.ok) {
				throw new Error('network response was not ok');
			}
			return response.json();
	})
	.then(data => {
			if (data == "stopped") {
				handleStopped()
			}
			if (data == "running") {
				handleRunning()
			}
	}).catch(error => {
			console.error('error fetching api status:', error);
				$('#errors').show().html('<p>An error occurred while fetching api status.</p>');
	})
}


$(document).ready(function() {
	fetchStatus()
});
