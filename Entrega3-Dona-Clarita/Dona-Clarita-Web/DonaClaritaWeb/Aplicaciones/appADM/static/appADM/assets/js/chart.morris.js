$(function(){
	
	/* Morris Area Chart */
	
	window.mA = Morris.Area({
	    element: 'morrisArea',
	    data: [

	        { y: '2015', a: 500000},
	        { y: '2016', a: 1000000},
	        { y: '2017', a: 2000000},
	        { y: '2018', a: 1200000},
	        { y: '2019', a: 2500000},
	    ],
	    xkey: 'y',
	    ykeys: ['a'],
	    labels: ['Ingresos'],
	    lineColors: ['#1b5a90'],
	    lineWidth: 2,
		
     	fillOpacity: 0.5,
	    gridTextSize: 10,
	    hideHover: 'auto',
	    resize: true,
		redraw: true
	});
	
	/* Morris Line Chart */
	
	window.mL = Morris.Line({
	    element: 'morrisLine',
	    data: [
	        { y: '2015', a: 100, b: 30},
	        { y: '2016', a: 100,  b: 60},
	        { y: '2017', a: 140,  b: 120},
	        { y: '2018', a: 140,  b: 80},
	        { y: '2019', a: 150,  b: 150},
	    ],
	    xkey: 'y',
	    ykeys: ['a', 'b'],
	    labels: ['Disponibles', 'Utilizadas'],
	    lineColors: ['#1b5a90','#ff9d00'],
	    lineWidth: 1,
	    gridTextSize: 10,
	    hideHover: 'auto',
	    resize: true,
		redraw: true
	});
	$(window).on("resize", function(){
		mA.redraw();
		mL.redraw();
	});

});