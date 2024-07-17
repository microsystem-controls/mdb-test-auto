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
		$('.table').empty()
		$('.table').append(
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
										step: 10,
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
	}
}
var last_data;
var denominations;
var result_table;

$(document).ready(function() {
	$('#device-info').click(function() {
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
	});
});
