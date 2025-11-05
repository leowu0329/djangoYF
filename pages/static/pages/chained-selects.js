async function fetchJson(url) {
  try {
    const resp = await fetch(url, { credentials: 'same-origin' });
    if (!resp.ok) {
      let errorMsg = `HTTP ${resp.status} 錯誤`;
      if (resp.status === 404) {
        errorMsg = '找不到請求的資源（404錯誤），請檢查URL路徑是否正確';
      } else if (resp.status === 400) {
        errorMsg = '請求參數錯誤（400錯誤）';
      } else if (resp.status === 500) {
        errorMsg = '伺服器內部錯誤（500錯誤）';
      }
      
      // 嘗試解析JSON錯誤消息
      try {
        const errorData = await resp.json();
        if (errorData && errorData.error) {
          errorMsg = errorData.error;
        }
      } catch (e) {
        // 如果不是JSON，忽略
      }
      
      console.error('載入資料失敗:', errorMsg);
      return null;
    }
    
    const data = await resp.json();
    // 檢查是否有錯誤消息
    if (data && data.error) {
      console.error('伺服器返回錯誤:', data.error);
      return null;
    }
    return data;
  } catch (err) {
    console.error('載入資料時發生錯誤:', err.message);
    return null;
  }
}

function clearOptions(select) {
  select.innerHTML = '<option value="">---</option>';
}

function fillOptions(select, items) {
  clearOptions(select);
  if (!items) return;
  for (const it of items) {
    const opt = document.createElement('option');
    opt.value = it.id;
    opt.textContent = it.name;
    select.appendChild(opt);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const citySelect = document.querySelector('#id_city');
  const townshipSelect = document.querySelector('#id_township');

  if (!citySelect || !townshipSelect) return;

  // 當 city 改變 -> 載入對應鄉鎮，並清空 township 選擇
  citySelect.addEventListener('change', async (e) => {
    const cityId = e.target.value;
    clearOptions(townshipSelect);
    if (!cityId) return;
    const data = await fetchJson(`/ajax/load-townships/?city_id=${encodeURIComponent(cityId)}`);
    if (data) fillOptions(townshipSelect, data);
  });

  // 當 township 改變 -> 取得該 township 的 city 並選上（反向同步）
  townshipSelect.addEventListener('change', async (e) => {
    const townshipId = e.target.value;
    if (!townshipId) return;
    const data = await fetchJson(`/ajax/get-city-for-township/?township_id=${encodeURIComponent(townshipId)}`);
    if (data && data.id) {
      // 避免觸發 city 的 change 事件產生循環：先暫時移除 handler
      const evHandlers = citySelect.onchange;
      citySelect.value = data.id;
      // 重新載入該 city 的 townships 並確保 township 仍被選中
      const towns = await fetchJson(`/ajax/load-townships/?city_id=${encodeURIComponent(data.id)}`);
      if (towns) {
        fillOptions(townshipSelect, towns);
        townshipSelect.value = townshipId;
      }
      if (evHandlers) citySelect.onchange = evHandlers;
    }
  });

  // 頁面初次載入（若表單已有預設 city，預先載入對應的 townships）
  if (citySelect.value) {
    (async () => {
      const towns = await fetchJson(`/ajax/load-townships/?city_id=${encodeURIComponent(citySelect.value)}`);
      if (towns) fillOptions(townshipSelect, towns);
    })();
  }
});