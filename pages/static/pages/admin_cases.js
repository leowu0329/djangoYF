(function() {
  function ready(fn) {
    if (document.readyState !== 'loading') {
      fn();
    } else {
      document.addEventListener('DOMContentLoaded', fn);
    }
  }

  ready(function() {
    var citySelect = document.getElementById('id_city');
    var townshipSelect = document.getElementById('id_township');
    if (!citySelect || !townshipSelect) return;

    console.log('[admin_cases] loaded');

    function clearTownships() {
      while (townshipSelect.firstChild) townshipSelect.removeChild(townshipSelect.firstChild);
      var opt = document.createElement('option');
      opt.value = '';
      opt.textContent = '---------';
      townshipSelect.appendChild(opt);
    }

    function parseJsonSafe(res) {
      var ct = res.headers.get('content-type') || '';
      if (!ct.includes('application/json')) {
        return res.text().then(function(t){
          var errorMsg = '伺服器回應非JSON格式，可能是404錯誤頁面';
          if (res.status === 404) {
            errorMsg = '找不到請求的資源（404錯誤），請檢查URL路徑是否正確';
          }
          throw new Error(errorMsg);
        });
      }
      return res.json();
    }

    function showError(message) {
      console.error('[admin_cases] 錯誤:', message);
      // 可以選擇在這裡顯示用戶友好的錯誤消息
      // 例如：alert('載入鄉鎮資料失敗：' + message);
    }

    function loadTownships(cityId) {
      if (!cityId) {
        clearTownships();
        return;
      }
      // 嘗試多個可能路徑，避免不同路由前綴造成 404
      var base = window.location.origin;
      var djangoOrigin = (window.__DJANGO_ORIGIN__ || 'http://localhost:8000').replace(/\/$/, '');
      var qs = '?city_id=' + encodeURIComponent(cityId) + '&_=' + Date.now();
      var candidates = [
        base + '/ajax/load-townships/' + qs,
        base + '/cases/ajax/load-townships/' + qs,
        djangoOrigin + '/ajax/load-townships/' + qs
      ];

      function tryFetch(index) {
        if (index >= candidates.length) {
          var errorMsg = '所有請求端點都失敗，無法載入鄉鎮資料';
          console.error('[admin_cases]', errorMsg);
          showError(errorMsg);
          clearTownships();
          return;
        }
        var url = candidates[index];
        console.log('[admin_cases] 嘗試請求:', url);
        var isCrossOrigin = !url.startsWith(base);
        fetch(url, isCrossOrigin ? { mode: 'cors' } : { credentials: 'same-origin' })
          .then(function(res) {
            if (!res.ok) {
              var errorMsg = 'HTTP ' + res.status;
              if (res.status === 404) {
                errorMsg = '找不到請求的資源（404錯誤）';
              } else if (res.status === 400) {
                errorMsg = '請求參數錯誤（400錯誤）';
              } else if (res.status === 500) {
                errorMsg = '伺服器內部錯誤（500錯誤）';
              }
              throw new Error(errorMsg);
            }
            return parseJsonSafe(res);
          })
          .then(function(items) {
            if (items && items.error) {
              throw new Error(items.error);
            }
            clearTownships();
            if (Array.isArray(items)) {
              items.forEach(function(item) {
                var opt = document.createElement('option');
                opt.value = item.id;
                opt.textContent = item.name;
                townshipSelect.appendChild(opt);
              });
            }
          })
          .catch(function(err) {
            var errorMsg = '載入鄉鎮資料失敗: ' + err.message;
            console.warn('[admin_cases] 端點失敗，嘗試下一個:', url, errorMsg);
            showError(errorMsg);
            tryFetch(index + 1);
          });
      }

      tryFetch(0);
    }

    // 初次載入若 city 有值，載入對應鄉鎮
    if (citySelect.value) {
      loadTownships(citySelect.value);
    } else {
      clearTownships();
    }

    citySelect.addEventListener('change', function() {
      console.log('[admin_cases] city changed:', citySelect.value);
      // 變更縣市時，清空鄉鎮並重新載入
      clearTownships();
      loadTownships(citySelect.value);
    });
  });
})();


