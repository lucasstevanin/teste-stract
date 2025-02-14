// Filtro de tabela
function sortTable(thElement) {
    var columnIndex = thElement.getAttribute("data-column");
    var table = document.getElementById("insightsTable");
    var rows = Array.from(table.getElementsByTagName("tr")).slice(1);
    var isNumeric = !isNaN(rows[0].cells[columnIndex]?.textContent.trim().replace("R$ ", "").replace(",", "."));

    var ascending = table.getAttribute("data-sort-column") != columnIndex || table.getAttribute("data-sort-order") === "desc";
    table.setAttribute("data-sort-column", columnIndex);
    table.setAttribute("data-sort-order", ascending ? "asc" : "desc");

    rows.sort(function (rowA, rowB) {
        var cellA = rowA.cells[columnIndex].textContent.trim().replace("R$ ", "").replace(",", ".");
        var cellB = rowB.cells[columnIndex].textContent.trim().replace("R$ ", "").replace(",", ".");

        if (isNumeric) {
            return ascending ? (parseFloat(cellA) - parseFloat(cellB)) : (parseFloat(cellB) - parseFloat(cellA));
        } else {
            return ascending ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
        }
    });

    var tbody = table.getElementsByTagName("tbody")[0];
    rows.forEach(row => tbody.appendChild(row));
}