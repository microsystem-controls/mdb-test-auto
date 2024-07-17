class Denomination{
	constructor(routing, credit){
		this.routing = routing;
		this.credit = credit;
	}
}

class Table{
	constructor(denominations){
		this.denominations = denominations;
	}
	initialise(){
		
	}
}
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
				denominations = data.coin_type_routing.map((i) => new Denomination(i, data.coin_type_credit[i] * data.coin_scaling_factor));
				result_table = new Table(denominations);
				result_table.initialise()
			})
			.catch(error => {
				console.error('Error fetching device info:', error);
				document.getElementById('device-info').innerHTML = '<p>An error occurred while fetching device info.</p>';
			});
	});
});
