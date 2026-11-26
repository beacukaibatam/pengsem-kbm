import re

with open('dashboard_pegawai.html', 'r', encoding='utf-8') as f:
    html = f.read()

replacement_js = '''        // ================= KONSOL OPERATOR LIVE CHAT WHATSAPP RESMI (+62 851-4490-1346) =================
        let allConversations = {};
        let activeChatPhone = null;
        let chatPollingInterval = null;

        function openLiveChatModal(targetPhone = null) {
            const modal = document.getElementById('liveChatModal');
            if (modal) modal.style.display = 'flex';
            loadLiveChatConversations(targetPhone);
            
            // Polling percakapan setiap 3 detik
            if (chatPollingInterval) clearInterval(chatPollingInterval);
            chatPollingInterval = setInterval(() => {
                if (document.getElementById('liveChatModal').style.display === 'flex') {
                    loadLiveChatConversations(activeChatPhone, true);
                }
            }, 3000);
        }

        function closeLiveChatModal() {
            const modal = document.getElementById('liveChatModal');
            if (modal) modal.style.display = 'none';
            if (chatPollingInterval) {
                clearInterval(chatPollingInterval);
                chatPollingInterval = null;
            }
        }

        function openChatFromDrawer() {
            if (!selectedPermohonanId) return;
            const item = allPermohonan.find(p => p.id === selectedPermohonanId);
            if (!item) return;
            const phone = item.no_wa_pengirim || item.no_wa_pemohon || '';
            openLiveChatModal(phone);
        }

        async function loadLiveChatConversations(selectPhone = null, isSilent = false) {
            try {
                const res = await fetch('/api/wa/conversations');
                if (res.ok) {
                    allConversations = await res.json();
                    renderConversationList();
                    if (selectPhone) {
                        selectConversation(selectPhone);
                    } else if (!activeChatPhone && Object.keys(allConversations).length > 0) {
                        selectConversation(Object.keys(allConversations)[0]);
                    } else if (activeChatPhone && isSilent) {
                        renderActiveChatMessages();
                    }
                }
            } catch (e) {
                console.warn('Gagal memuat obrolan WA:', e);
            }
        }

        function renderConversationList() {
            const container = document.getElementById('conversationListContainer');
            if (!container) return;
            const search = (document.getElementById('searchContactInput')?.value || '').toLowerCase();
            
            container.innerHTML = '';
            const phones = Object.keys(allConversations);
            
            if (phones.length === 0) {
                container.innerHTML = '<div style="padding:20px; text-align:center; color:#94A3B8; font-size:0.80rem;">Belum ada percakapan masuk</div>';
                return;
            }

            phones.forEach(phone => {
                const conv = allConversations[phone];
                const nama = conv.nama || ('Pemohon (' + phone + ')');
                const lastMsg = conv.messages && conv.messages.length > 0 ? conv.messages[conv.messages.length - 1] : { text: '-', timestamp: '' };
                
                if (search && !nama.toLowerCase().includes(search) && !phone.includes(search)) {
                    return;
                }

                const isActive = (activeChatPhone === phone);
                const itemDiv = document.createElement('div');
                itemDiv.style.cssText = 'padding:10px 12px; margin-bottom:4px; border-radius:8px; cursor:pointer; transition:all 0.15s; background:' + (isActive ? '#E2E8F0' : '#FFFFFF') + '; border:1px solid ' + (isActive ? '#94A3B8' : '#E2E8F0') + '; display:flex; gap:10px; align-items:center;';
                itemDiv.onclick = () => selectConversation(phone);
                
                const prefix = lastMsg.sender === 'officer' ? '👮‍♂️ Anda: ' : (lastMsg.sender === 'bot' ? '🤖 Bot: ' : '');
                const timeStr = lastMsg.timestamp ? lastMsg.timestamp.slice(11, 16) : '';
                
                itemDiv.innerHTML = 
                    '<div style="width:38px; height:38px; border-radius:50%; background:#059669; color:#FFFFFF; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.9rem; flex-shrink:0;">' +
                        nama.charAt(0).toUpperCase() +
                    '</div>' +
                    '<div style="flex:1; overflow:hidden;">' +
                        '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">' +
                            '<span style="font-weight:700; font-size:0.82rem; color:#0F172A; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">' + nama + '</span>' +
                            '<span style="font-size:0.65rem; color:#64748B;">' + timeStr + '</span>' +
                        '</div>' +
                        '<div style="font-size:0.72rem; color:#64748B; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">' +
                            prefix + lastMsg.text +
                        '</div>' +
                    '</div>';
                container.appendChild(itemDiv);
            });
        }

        function filterContactList() {
            renderConversationList();
        }

        function selectConversation(phone) {
            let cleanPhone = phone.replace('+', '').replace('-', '').replace(/\\s/g, '');
            if (cleanPhone.startsWith('08')) cleanPhone = '628' + cleanPhone.slice(2);
            activeChatPhone = cleanPhone;
            
            // Update Top Bar
            const conv = allConversations[activeChatPhone] || { nama: 'Pemohon (' + activeChatPhone + ')', nomor: activeChatPhone, messages: [] };
            document.getElementById('activeChatName').innerText = conv.nama || 'Pemohon WhatsApp';
            document.getElementById('activeChatPhone').innerText = 'Nomor WhatsApp: +' + activeChatPhone;
            
            const badge = document.getElementById('activeChatBadge');
            badge.innerText = '● Terhubung Langsung';
            badge.style.background = '#DCFCE7';
            badge.style.color = '#15803D';

            renderConversationList();
            renderActiveChatMessages();
        }

        function renderActiveChatMessages() {
            const body = document.getElementById('operatorChatBody');
            if (!body || !activeChatPhone) return;
            const conv = allConversations[activeChatPhone];
            if (!conv || !conv.messages || conv.messages.length === 0) {
                body.innerHTML = '<div style="margin:auto; text-align:center; color:#94A3B8; font-size:0.85rem;">Belum ada riwayat pesan untuk kontak ini.<br>Ketik pesan di bawah untuk memulai chat resmi via WhatsApp.</div>';
                return;
            }

            body.innerHTML = '';
            conv.messages.forEach(msg => {
                const isOfficer = (msg.sender === 'officer');
                const isBot = (msg.sender === 'bot');
                const isUser = (msg.sender === 'user');

                const row = document.createElement('div');
                row.style.cssText = 'display:flex; flex-direction:column; align-items:' + (isUser ? 'flex-start' : 'flex-end') + '; margin-bottom:8px;';

                const senderLabel = isOfficer ? '👮‍♂️ Petugas Bea Cukai' : (isBot ? '🤖 Bot Otomatis' : '👤 Pemohon');
                const bg = isOfficer ? '#DCFCE7' : (isBot ? '#E0F2FE' : '#FFFFFF');
                const border = isOfficer ? '#86EFAC' : (isBot ? '#BAE6FD' : '#CBD5E1');

                row.innerHTML = 
                    '<span style="font-size:0.65rem; color:#64748B; margin-bottom:2px; font-weight:600;">' + senderLabel + ' &bull; ' + (msg.timestamp || '') + '</span>' +
                    '<div style="max-width:75%; padding:10px 14px; border-radius:' + (isUser ? '4px 14px 14px 14px' : '14px 4px 14px 14px') + '; background:' + bg + '; border:1px solid ' + border + '; color:#0F172A; font-size:0.82rem; line-height:1.45; word-break:break-word; box-shadow:0 1px 2px rgba(0,0,0,0.05);">' +
                        msg.text.replace(/\\n/g, '<br>') +
                    '</div>';
                body.appendChild(row);
            });

            body.scrollTop = body.scrollHeight;
        }

        function insertQuickReply(text) {
            const input = document.getElementById('txtOperatorMessage');
            if (input) {
                input.value = text;
                input.focus();
            }
        }

        async function sendOperatorMessage() {
            if (!activeChatPhone) {
                alert('Silakan pilih kontak pemohon terlebih dahulu di sisi kiri.');
                return;
            }
            const input = document.getElementById('txtOperatorMessage');
            const text = (input?.value || '').trim();
            if (!text) return;

            const btn = document.getElementById('btnSendOperator');
            if (btn) btn.disabled = true;

            try {
                const res = await fetch('/api/wa/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        to: activeChatPhone,
                        text: text,
                        officer_name: 'Petugas Bea Cukai Batam'
                    })
                });
                const result = await res.json();
                if (result.status === 'success') {
                    input.value = '';
                    await loadLiveChatConversations(activeChatPhone, true);
                } else {
                    alert('Gagal mengirim WhatsApp: ' + (result.message || 'Error'));
                }
            } catch (e) {
                alert('Terjadi kesalahan koneksi server: ' + e.message);
            } finally {
                if (btn) btn.disabled = false;
            }
        }
'''

idx = html.find('// ================= SIMULATOR BOT WHATSAPP =================')
if idx != -1:
    end_idx = html.find('function promptChangeSenderNumber()', idx)
    if end_idx == -1:
        end_idx = html.find('</script>', idx)
    html = html[:idx] + replacement_js + '\n\n        ' + html[end_idx:]
    print('Replaced simulator JS with Live Chat Operator Console JS!')
else:
    print('Pattern // ================= SIMULATOR BOT WHATSAPP ================= not found!')

with open('dashboard_pegawai.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved updated dashboard_pegawai.html')
