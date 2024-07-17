class Denomination{
	constructor(routing, credit){
		this.routing = routing;
		this.credit = credit;
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
					$('<tr class="table-success">').append(
						[
							$('<th scope="row">').text("1"),
							$('<th>').text(this.serial_number),
							$('<th>').text(this.denominations[0].credit),
							$('<th>').text(0),
						]
					)
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
