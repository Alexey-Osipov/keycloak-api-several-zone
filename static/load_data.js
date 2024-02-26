fetch('/static/data.json')
    .then(response => response.json())
    .then(data => {
        const zonesContainer = document.getElementById('zones_container');
        const realmsSelect = document.getElementById('realm');

        data.servers.forEach(server => {
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.name = 'server';
            checkbox.value = server.value;

            const label = document.createElement('label');
            label.textContent = server.name;

            zones_container.appendChild(checkbox);
            zones_container.appendChild(label);
            zones_container.appendChild(document.createElement('br'));
        });

        data.realms.forEach(realm => {
            const option = document.createElement('option');
            option.text = realm.name;
            option.value = realm.value;
            realmsSelect.appendChild(option);
        });
})
.catch(error => console.error('Ошибка загрузки данных:', error)); // Обработка ошибок