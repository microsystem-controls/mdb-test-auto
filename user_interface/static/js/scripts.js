class Denomination{
	constructor(routing, credit){
		this.routing = routing;
		this.credit = credit;
		this.cycle_count = 0;
	}
}

class Table{
	constructor(denominations, serial_number){
		this.denominations = denominations;
		this.serial_number = serial_number;
	}
	initialiseCycleSelection(){
		$('#result-table').empty()
		$('#result-table').append(
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
						$(`<tr id=${denomination.routing} class="table-success">`).append([
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
					const resulting_denominations = result_table.denominations.filter(denomination => denomination.cycle_count != 0)
					if (resulting_denominations.length == 0){
						alert('in order to run, please specify a counter > 0 for at least one denomination')
					}
					else{
						const denominations_for_export = resulting_denominations.reduce((dictionary, denomination) => {
							dictionary[denomination.routing] = denomination.cycle_count;
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
					.then((json) => console.log(json))
					.catch(error => {
							console.error('error running cycles with denominations', error);
					})
					}
			})
		)
	}
}
var last_data;
var denominations;
var result_table;

$(document).ready(function() {
		fetch('/api/device_info')
			.then(response => {
				if (!response.ok) {
					throw new Error('Network response was not ok');
				}
				return response.json();
			})
			.then(data => {
				last_data = data;
				denominations = data.coin_type_routing.map((i) => new Denomination(i, data.coin_type_credit[i] * data.coin_scaling_factor));
				result_table = new Table(denominations, data.serial_number);
				result_table.initialiseCycleSelection()
			})
			.catch(error => {
				console.error('Error fetching device info:', error);
				document.getElementById('device-info').innerHTML = '<p>An error occurred while fetching device info.</p>';
		});
	// $('#device-info').click(function() {
	// });
});
