function aplicarFiltro() {
    var carrera = document.getElementById('filtro-carrera').value;
    var graduacion = document.getElementById('filtro-graduacion').value;
    var salarioMin = document.getElementById('filtro-salario-min').value;
    var salarioMax = document.getElementById('filtro-salario-max').value;
    var continuacion = document.getElementById('filtro-continuacion').value;
    var tiempoEmpleo = document.getElementById('filtro-tiempo-empleo').value;

    fetch('/filtrar_egresados', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            carrera: carrera,
            graduacion: graduacion,
            salarioMin: salarioMin,
            salarioMax: salarioMax,
            continuacion: continuacion,
            tiempoEmpleo: tiempoEmpleo
        })
    })
    .then(response => response.json())
    .then(data => {
        // Limpiar la tabla de resultados anteriormente mostrados
        const tableBody = document.getElementById('tabla-egresados-body');
        tableBody.innerHTML = '';
    
        // Recorrer los datos filtrados y agregarlos a la tabla
        data.forEach(egresado => {
            console.log(egresado)
            const row = document.createElement('tr');
            let continuaEstudios = egresado[5];
            let continuidad;

            if (continuaEstudios === 1) {
                continuidad = 'Sí';
            } else {
                continuidad = 'No';
            }
            row.innerHTML = `
                <td>${egresado[0]}</td>
                <td>${egresado[1]}</td>
                <td>${egresado[2]}</td>
                <td>${egresado[3]}</td>
                <td>${egresado[4]}</td>
                <td>${continuidad}</td>
                <td>${egresado[6]}</td>
            `;
            tableBody.appendChild(row);
        });
    })
    .catch(error => {
        // Manejar cualquier error que ocurra durante la solicitud
        console.error('Error al obtener datos filtrados:', error);
    });

}


function limpiarFiltros() {
    document.getElementById('filtro-carrera').value = '';
    document.getElementById('filtro-graduacion').value = '';
    document.getElementById('filtro-salario-min').value = '';
    document.getElementById('filtro-salario-max').value = '';
    document.getElementById('filtro-continuacion').value = '';
    document.getElementById('filtro-tiempo-empleo').value = '';
}

function generarGrafico() {
    // Obtener las filas de la tabla de egresados
    const tablaEgresados = document.getElementById('tabla-egresados-body');
    const filas = tablaEgresados.querySelectorAll('tr');

    // Inicializar arrays para almacenar carreras y salarios promedio
    const carreras = [];
    const salarios = [];

    // Iterar sobre las filas de la tabla para obtener los datos
    filas.forEach(fila => {
        // Obtener los datos de la fila
        const datos = fila.querySelectorAll('td');
        const carrera = datos[2].innerText; // Carrera en la tercera columna
        const salario = parseFloat(datos[4].innerText); // Salario en la quinta columna (convertido a número)

        // Verificar si la carrera ya está en la lista de carreras
        const index = carreras.indexOf(carrera);
        if (index !== -1) {
            // La carrera ya existe, agregar el salario al array correspondiente
            salarios[index].push(salario);
        } else {
            // La carrera no existe, agregarla a la lista de carreras y crear un nuevo array de salarios
            carreras.push(carrera);
            salarios.push([salario]);
        }
    });

    // Calcular el salario promedio para cada carrera
    const salariosPromedio = salarios.map(salarioArray => {
        const sum = salarioArray.reduce((acc, curr) => acc + curr, 0);
        return sum / salarioArray.length;
    });

    // Crear el objeto de datos para Plotly
    const data = [{
        x: carreras,
        y: salariosPromedio,
        type: 'bar'
    }];

    // Configurar el diseño del gráfico
    const layout = {
        title: 'Salario Promedio por Carrera',
        xaxis: {
            title: 'Carrera'
        },
        yaxis: {
            title: 'Salario Promedio'
        }
    };

    // Abrir una nueva ventana y mostrar el gráfico en ella
    const graficoWindow = window.open('', '_blank', 'width=800,height=600');
    graficoWindow.document.write('<html><head><title>Gráfico</title>');
    graficoWindow.document.write('<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>');
    graficoWindow.document.write('</head><body>');
    graficoWindow.document.write('<div id="grafico-container"></div>');
    graficoWindow.document.write('<script>');
    graficoWindow.document.write(`Plotly.newPlot('grafico-container', ${JSON.stringify(data)}, ${JSON.stringify(layout)});`);
    graficoWindow.document.write('</script>');
    graficoWindow.document.write('</body></html>');
}



