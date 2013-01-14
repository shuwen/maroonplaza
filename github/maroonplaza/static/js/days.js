$(function() {
	// gets dates for the current day
	var d1 = new Date();
	var d2 = new Date();
	var d3 = new Date();
	var d4 = new Date();
	var d5 = new Date();
	var d6 = new Date();
	var d7 = new Date();
	// give the day numbe
	var daynum = new Array;
	daynum[0] = d1.getDate();
	daynum[1] = d2.getDate() + 1;
	daynum[2] = d3.getDate() + 2;
	daynum[3] = d4.getDate() + 3;
	daynum[4] = d5.getDate() + 4;
	daynum[5] = d6.getDate() + 5;
	daynum[6] = d7.getDate() + 6;
	//month Array
	var month=new Array();
	month[0]="January";
	month[1]="February";
	month[2]="March";
	month[3]="April";
	month[4]="May";
	month[5]="June";
	month[6]="July";
	month[7]="August";
	month[8]="September";
	month[9]="October";
	month[10]="November";
	month[11]="December";
	//current month
	var currentMonth = month[d1.getMonth()];

	var heading = $('#main th h1');
	for(var i=0; i<7; i++) {
		heading[i].html(daynum[i]);
	}
});