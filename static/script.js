    // On page load, set up DataTables
    $(document).ready(function(){
      $('#cardsTable').DataTable({
          "order": [[4, "desc"]],
          "searching": true,
          "paging": true,   // Enables pagination
          "lengthMenu": [10, 25, 50, 100], // Options for rows per page
        "pageLength": 25,  // Default rows per page
        "columnDefs": [
            { "targets": 2, "visible": false } // Hides the "Prints" column (index 2)
        ]
    });

      // At page load, see if we had stored a theme previously
      const storedTheme = localStorage.getItem('selectedTheme');
      if(storedTheme) {
        setTheme(storedTheme);
        document.getElementById('themeSelect').value = storedTheme;
      }
    });

    // Theme switching script
    const themeSelect = document.getElementById('themeSelect');
    themeSelect.addEventListener('change', function() {
      const chosen = this.value;
      localStorage.setItem('selectedTheme', chosen);
      setTheme(chosen);
    });

    function setTheme(selectedTheme) {
      // Remove existing theme classes
      document.body.classList.remove(
        'dark-theme',
        'psychedelic-theme',
        'purple-theme',
        'acid-theme',
        'matrix-theme'
      );

      // Add the chosen theme class if not "light"
      if (selectedTheme === 'dark') {
        document.body.classList.add('dark-theme');
      } else if (selectedTheme === 'psychedelic') {
        document.body.classList.add('psychedelic-theme');
      } else if (selectedTheme === 'purple') {
        document.body.classList.add('purple-theme');
      } else if (selectedTheme === 'acid') {
        document.body.classList.add('acid-theme');
      } else if (selectedTheme === 'matrix') {
        document.body.classList.add('matrix-theme');
      }
      // else, remain in default "light" theme
    }