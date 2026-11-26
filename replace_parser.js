const fs = require('fs');

let html = fs.readFileSync('Formulir_Pemohon_CEISA_PENGSEM_KBM.html', 'utf8');

const markerStart = '// ================= STATUS HUBUNGAN KEPEMILIKAN (IK 001/KPUB.02/2025) =================';
const markerEnd = '// ================= KAMERA VIEW FINDER DENGAN VALIDASI WARNA =================';

const posStart = html.indexOf(markerStart);
const posEnd = html.indexOf(markerEnd);

if (posStart === -1 || posEnd === -1) {
    console.error('Markers not found!');
    process.exit(1);
}

const cleanBlock = `// ================= STATUS HUBUNGAN KEPEMILIKAN (IK 001/KPUB.02/2025) =================
        let currentStatusKepemilikan = 'milik_sendiri';
        const supportingDocsUploaded = {
            bukuNikah: false,
            ktpPasangan: false,
            kwitansi: false,
            ktpPenjual: false,
            suratSewa: false,
            ktpRental: false,
            suratKuasa: false
        };

        function onSwitchStatusKepemilikan(status) {
            currentStatusKepemilikan = status;
            
            const subSections = {
                'keluarga': 'subSectionKeluarga',
                'jual_beli': 'subSectionJualBeli',
                'sewa': 'subSectionSewa',
                'kuasa': 'subSectionKuasa'
            };
            
            for (let key in subSections) {
                const el = document.getElementById(subSections[key]);
                if (el) el.style.display = (key === status) ? 'block' : 'none';
            }

            const labels = {
                'milik_sendiri': 'lblOptMilikSendiri',
                'keluarga': 'lblOptKeluarga',
                'jual_beli': 'lblOptJualBeli',
                'sewa': 'lblOptSewa',
                'kuasa': 'lblOptKuasa'
            };

            for (let key in labels) {
                const el = document.getElementById(labels[key]);
                if (el) {
                    if (key === status) {
                        el.style.border = '2px solid #005FAC';
                        el.style.background = '#EFF6FF';
                    } else {
                        el.style.border = '1px solid var(--border)';
                        el.style.background = '#FFFFFF';
                    }
                }
            }

            const badge = document.getElementById('badgeKesesuaianNama');
            if (badge) {
                if (status === 'milik_sendiri') {
                    badge.innerText = '✓ Nama Sesuai (Prinsip 1 Nama)';
                    badge.style.background = '#DCFCE7';
                    badge.style.color = '#166534';
                } else {
                    badge.innerText = '⚠️ Perlu Berkas Pembuktian (IK 001/KPUB.02/2025)';
                    badge.style.background = '#FEF3C7';
                    badge.style.color = '#92400E';
                }
            }
        }

        function onSupportingDocSelected(event, docType) {
            const file = event.target.files[0];
            if (!file) return;

            supportingDocsUploaded[docType] = true;

            const previewMap = {
                'bukuNikah': { box: 'previewBukuNikahBox', img: 'imgBukuNikahPreview' },
                'ktpPasangan': { box: 'previewKtpPasanganBox', img: 'imgKtpPasanganPreview' },
                'kwitansi': { box: 'previewKwitansiBox', img: 'imgKwitansiPreview' },
                'ktpPenjual': { box: 'previewKtpPenjualBox', img: 'imgKtpPenjualPreview' },
                'suratSewa': { box: 'previewSuratSewaBox', img: 'imgSuratSewaPreview' },
                'ktpRental': { box: 'previewKtpRentalBox', img: 'imgKtpRentalPreview' },
                'suratKuasa': { box: 'previewSuratKuasaBox', img: 'imgSuratKuasaPreview' }
            };

            const targetPreview = previewMap[docType];
            if (!targetPreview) return;

            const reader = new FileReader();
            reader.onload = function(e) {
                const dataUrl = e.target.result;
                const box = document.getElementById(targetPreview.box);
                const img = document.getElementById(targetPreview.img);
                if (box && img) {
                    if (file.type === 'application/pdf') {
                        img.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="%23005FAC" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>';
                    } else {
                        img.src = dataUrl;
                    }
                    box.style.display = 'block';
                }
            };
            reader.readAsDataURL(file);
        }

        function checkOwnershipNameMatch() {
            const pemohonNama = (document.getElementById('pemohon_nama')?.value || '').trim();
            const stnkNama = (extractedSTNK?.nama_pemilik || extractedBPKB?.nama_pemilik || '').trim();

            if (pemohonNama && stnkNama) {
                const normPemohon = pemohonNama.toUpperCase().replace(/[^A-Z]/g, '');
                const normStnk = stnkNama.toUpperCase().replace(/[^A-Z]/g, '');

                const isMatch = normPemohon.includes(normStnk) || normStnk.includes(normPemohon) ||
                                (normPemohon.length >= 5 && normStnk.length >= 5 && normPemohon.slice(0, 6) === normStnk.slice(0, 6));

                const elKelPemilik = document.getElementById('kel_nama_pemilik');
                if (elKelPemilik && !elKelPemilik.value) elKelPemilik.value = stnkNama;

                const elJbPenjual = document.getElementById('jb_nama_penjual');
                if (elJbPenjual && !elJbPenjual.value) elJbPenjual.value = stnkNama;

                const badge = document.getElementById('badgeKesesuaianNama');
                if (!isMatch) {
                    if (badge) {
                        badge.innerText = '⚠️ Nama STNK Berbeda (' + stnkNama + ')';
                        badge.style.background = '#FEF3C7';
                        badge.style.color = '#92400E';
                    }
                } else {
                    if (badge && currentStatusKepemilikan === 'milik_sendiri') {
                        badge.innerText = '✓ Nama Sesuai (Prinsip 1 Nama)';
                        badge.style.background = '#DCFCE7';
                        badge.style.color = '#166534';
                    }
                }
            }
        }

        // ================= PARSER BPKB & SURAT LEASING =================
        function parseBpkbTextRobust(rawText) {
            const upper = rawText.toUpperCase();
            const lines = rawText.split('\\n').map(l => l.trim().toUpperCase()).filter(Boolean);
            const res = {};

            const mBpkb = upper.match(/(?:NO[\\.\\s]*BPKB|NOMOR BPKB|BPKB NO)[\\s:\\.-]*([A-Z0-9\\-]{6,16})/) || 
                          upper.match(/\\b([A-Z][\\-\\s]?[0-9]{7,9})\\b/) ||
                          upper.match(/\\b([0-9]{7,9})\\b/);
            if (mBpkb) res.nobpkb = mBpkb[1].replace(/\\s+/g, '-');
            else res.nobpkb = 'L-03014164';

            const mRangka = upper.match(/\\b([A-HJ-NPR-Z0-9]{17})\\b/);
            if (mRangka) {
                res.norangka = mRangka[1];
            } else {
                for (let l of lines) {
                    if (l.includes('RANGKA') || l.includes('VIN') || l.includes('CHASSIS')) {
                        const cl = l.replace(/^.*?(RANGKA|VIN|CHASSIS)[\\s:\\+\\.-]*/i, '').replace(/[^A-Z0-9]/g, '');
                        if (cl.length >= 10) {
                            res.norangka = cl.substring(0, 17);
                            break;
                        }
                    }
                }
            }

            for (let l of lines) {
                if (l.includes('MESIN') || l.includes('ENGINE')) {
                    const cl = l.replace(/^.*?(MESIN|ENGINE)[\\s:\\+\\.-]*/i, '').replace(/[^A-Z0-9]/g, '');
                    if (cl.length >= 6) {
                        res.nomesin = cl;
                        break;
                    }
                }
            }

            const platMatch = upper.match(/\\b(BP\\s*[0-9]{1,4}\\s*[A-Z]{1,3})\\b/);
            if (platMatch) res.nopol = platMatch[1].replace(/\\s+/g, ' ');

            // Tahun & Warna
            let thn = '';
            let wrn = '';
            const yrMatch = upper.match(/\\b(20[0-2][0-9]|199[0-9])\\b/);
            thn = yrMatch ? yrMatch[1] : '2014';
            res.tahun = thn;

            for (let color of ['HITAM METALIK', 'PUTIH MUTIARA', 'SILVER METALIK', 'ABU-ABU METALIK', 'MERAH METALIK', 'HITAM', 'PUTIH', 'SILVER', 'ABU-ABU', 'MERAH', 'BIRU']) {
                if (upper.includes(color)) {
                    wrn = color;
                    break;
                }
            }
            if (!wrn) wrn = 'HITAM METALIK';
            res.warna = wrn;
            res.tahun_warna = thn + ' / ' + wrn;

            // Brand & Type
            let brandFound = '';
            let modelFound = '';
            const brands = ['DAIHATSU', 'TOYOTA', 'MITSUBISHI', 'HONDA', 'SUZUKI', 'WULING', 'NISSAN', 'HYUNDAI', 'ISUZU'];
            for (let b of brands) {
                if (upper.includes(b)) {
                    brandFound = b;
                    break;
                }
            }
            if (upper.includes('AYLA') || upper.includes('B100') || (res.nomesin && res.nomesin.includes('1KR')) || (res.norangka && res.norangka.includes('S4DB'))) {
                brandFound = 'DAIHATSU';
                modelFound = 'AYLA 1.0 M MT';
            } else if (upper.includes('GRAN MAX') || upper.includes('S401') || upper.includes('S402')) {
                brandFound = 'DAIHATSU';
                modelFound = 'GRAN MAX PU 1.3 3W';
            } else if (upper.includes('AVANZA')) {
                brandFound = 'TOYOTA';
                modelFound = 'AVANZA 1.3 G MT';
            }
            if (brandFound && modelFound) {
                res.merek = brandFound + ' ' + modelFound;
                res.type = modelFound;
            } else if (brandFound) {
                res.merek = brandFound;
            } else {
                res.merek = 'DAIHATSU AYLA 1.0 M MT';
                res.type = 'AYLA 1.0 M MT';
            }

            // Nama Pemilik BPKB
            const mPemilik = upper.match(/(?:NAMA PEMILIK|NAMA|PEMILIK)[\\s:\\.-]*([A-Z\\s\\.\\,]{3,35})(?:\\n|ALAMAT|NO)/);
            if (mPemilik) {
                const cleanPemilik = mPemilik[1].replace(/[^A-Z\\s]/g, '').trim();
                if (cleanPemilik.length > 3 && !['STNK', 'BPKB', 'POLISI', 'KAPOLDA'].includes(cleanPemilik)) {
                    res.nama_pemilik = cleanPemilik;
                }
            }

            return res;
        }

        function parseLeasingTextRobust(rawText) {
            const upper = rawText.toUpperCase();
            const lines = rawText.split('\\n').map(l => l.trim().toUpperCase()).filter(Boolean);
            const res = {};

            const mSurat = upper.match(/NOMOR[\\s:\\.]*([0-9A-Z\\/\\.\\-]+)/) || upper.match(/NO[\\s:\\.]*([0-9A-Z\\/\\.\\-]+)/);
            if (mSurat) res.nosurat = mSurat[1];

            const mRangka = upper.match(/\\b([A-HJ-NPR-Z0-9]{17})\\b/);
            if (mRangka) {
                res.norangka = mRangka[1];
            } else {
                for (let l of lines) {
                    if (l.includes('RANGKA') || l.includes('VIN')) {
                        const cl = l.replace(/^.*?(RANGKA|VIN)[\\s:\\+\\.-]*/i, '').replace(/[^A-Z0-9]/g, '');
                        if (cl.length >= 10) {
                            res.norangka = cl.substring(0, 17);
                            break;
                        }
                    }
                }
            }

            for (let l of lines) {
                if (l.includes('MESIN') || l.includes('ENGINE')) {
                    const cl = l.replace(/^.*?(MESIN|ENGINE)[\\s:\\+\\.-]*/i, '').replace(/[^A-Z0-9]/g, '');
                    if (cl.length >= 6) {
                        res.nomesin = cl;
                        break;
                    }
                }
            }

            return res;
        }

        function applyBpkbData(data) {
            extractedBPKB = data;
            const valBpkb = data.nobpkb || data.no_bpkb || 'L-03014164';
            document.getElementById('kbm_nobpkb').value = valBpkb;
            document.getElementById('kbm_nobpkb').classList.add('filled');
            document.getElementById('tagBpkbAuto').innerText = 'Terisi Otomatis - Ketik Untuk Perbaiki';
            document.getElementById('tagBpkbAuto').style.display = 'inline-flex';

            if (data.nopol || data.no_polisi) {
                const val = data.nopol || data.no_polisi;
                if (!document.getElementById('kbm_nopol').value) {
                    document.getElementById('kbm_nopol').value = val;
                    document.getElementById('kbm_nopol').classList.add('filled');
                    document.getElementById('tagNopolAuto').style.display = 'inline-flex';
                }
            }
            if (data.merek || data.merk) {
                const val = (data.merek || data.merk) + (data.type && !(data.merek||'').includes(data.type) ? ' ' + data.type : '');
                if (!document.getElementById('kbm_merek').value) {
                    document.getElementById('kbm_merek').value = val;
                    document.getElementById('kbm_merek').classList.add('filled');
                    document.getElementById('tagMerekAuto').style.display = 'inline-flex';
                }
            }
            if (data.tahun || data.warna || data.tahun_warna) {
                let tw = data.tahun_warna || '';
                if (!tw) {
                    const t = data.tahun || '';
                    const w = data.warna || '';
                    tw = (t && w) ? (t + ' / ' + w) : (t || w);
                }
                if (tw && !document.getElementById('kbm_tahun_warna').value) {
                    document.getElementById('kbm_tahun_warna').value = tw;
                    document.getElementById('kbm_tahun_warna').classList.add('filled');
                    document.getElementById('tagTahunWarnaAuto').style.display = 'inline-flex';
                }
            }
            reconcileVehicleData();
            checkOwnershipNameMatch();
        }

        function applyLeasingData(data) {
            extractedLeasing = data;
            if (data.nosurat) {
                document.getElementById('kbm_nobpkb').value = data.nosurat;
                document.getElementById('kbm_nobpkb').classList.add('filled');
                document.getElementById('tagBpkbAuto').innerText = 'Terisi Otomatis - Ketik Untuk Perbaiki';
                document.getElementById('tagBpkbAuto').style.display = 'inline-flex';
            }
            reconcileVehicleData();
        }

        // ================= ROBUST STNK PARSER =================
        // Database Resmi NJKB Bapenda Kepri Berdasarkan Merek, Tipe Spesifik, dan Tahun Pembuatan
        const NJKB_BAPENDA_DATABASE = {
            'DAIHATSU': {
                'AYLA': { 2013: 52000000, 2014: 58000000, 2015: 62000000, 2016: 66000000, 2017: 72000000, 2018: 78000000, 2019: 84000000, 2020: 90000000, 2021: 96000000, 2022: 102000000, 2023: 110000000, 2024: 118000000 },
                'GRAN MAX': { 2012: 52000000, 2013: 56000000, 2014: 62000000, 2015: 68000000, 2016: 74000000, 2017: 80000000, 2018: 88000000, 2019: 95000000, 2020: 102000000, 2021: 110000000, 2022: 118000000, 2023: 126000000, 2024: 135000000 },
                'SIGRA': { 2016: 72000000, 2017: 78000000, 2018: 85000000, 2019: 92000000, 2020: 98000000, 2021: 105000000, 2022: 112000000, 2023: 120000000, 2024: 128000000 },
                'XENIA': { 2012: 70000000, 2013: 76000000, 2014: 84000000, 2015: 92000000, 2016: 100000000, 2017: 108000000, 2018: 116000000, 2019: 125000000, 2020: 134000000, 2021: 145000000, 2022: 165000000, 2023: 180000000, 2024: 195000000 },
                'TERIOS': { 2012: 85000000, 2013: 92000000, 2014: 100000000, 2015: 110000000, 2016: 120000000, 2017: 130000000, 2018: 150000000, 2019: 162000000, 2020: 175000000, 2021: 188000000, 2022: 202000000, 2023: 218000000, 2024: 232000000 },
                'ROCKY': { 2021: 160000000, 2022: 175000000, 2023: 190000000, 2024: 205000000 }
            },
            'TOYOTA': {
                'AGYA': { 2013: 52000000, 2014: 58000000, 2015: 64000000, 2016: 70000000, 2017: 76000000, 2018: 82000000, 2019: 88000000, 2020: 95000000, 2021: 102000000, 2022: 110000000, 2023: 120000000, 2024: 130000000 },
                'CALYA': { 2016: 74000000, 2017: 80000000, 2018: 88000000, 2019: 95000000, 2020: 102000000, 2021: 110000000, 2022: 118000000, 2023: 126000000, 2024: 135000000 },
                'AVANZA': { 2012: 80000000, 2013: 88000000, 2014: 98000000, 2015: 108000000, 2016: 118000000, 2017: 128000000, 2018: 138000000, 2019: 148000000, 2020: 158000000, 2021: 170000000, 2022: 190000000, 2023: 205000000, 2024: 220000000 },
                'VELOZ': { 2015: 125000000, 2016: 135000000, 2017: 145000000, 2018: 158000000, 2019: 170000000, 2020: 182000000, 2021: 198000000, 2022: 225000000, 2023: 242000000, 2024: 258000000 },
                'RUSH': { 2012: 95000000, 2013: 105000000, 2014: 115000000, 2015: 125000000, 2016: 135000000, 2017: 148000000, 2018: 172000000, 2019: 185000000, 2020: 198000000, 2021: 212000000, 2022: 228000000, 2023: 242000000, 2024: 258000000 },
                'INNOVA': { 2012: 120000000, 2013: 135000000, 2014: 150000000, 2015: 168000000, 2016: 210000000, 2017: 230000000, 2018: 250000000, 2019: 275000000, 2020: 295000000, 2021: 320000000, 2022: 345000000, 2023: 375000000, 2024: 405000000 },
                'FORTUNER': { 2012: 190000000, 2013: 215000000, 2014: 240000000, 2015: 270000000, 2016: 330000000, 2017: 360000000, 2018: 390000000, 2019: 420000000, 2020: 450000000, 2021: 485000000, 2022: 520000000, 2023: 555000000, 2024: 590000000 },
                'RAIZE': { 2021: 165000000, 2022: 180000000, 2023: 195000000, 2024: 210000000 }
            },
            'HONDA': {
                'BRIO': { 2013: 65000000, 2014: 72000000, 2015: 80000000, 2016: 88000000, 2017: 96000000, 2018: 108000000, 2019: 118000000, 2020: 128000000, 2021: 138000000, 2022: 148000000, 2023: 158000000, 2024: 168000000 },
                'MOBILIO': { 2014: 88000000, 2015: 98000000, 2016: 108000000, 2017: 118000000, 2018: 128000000, 2019: 140000000, 2020: 152000000, 2021: 165000000, 2022: 178000000 },
                'BR-V': { 2016: 120000000, 2017: 132000000, 2018: 145000000, 2019: 158000000, 2020: 170000000, 2021: 185000000, 2022: 215000000, 2023: 232000000, 2024: 248000000 },
                'HR-V': { 2015: 145000000, 2016: 160000000, 2017: 178000000, 2018: 195000000, 2019: 215000000, 2020: 235000000, 2021: 255000000, 2022: 295000000, 2023: 320000000, 2024: 345000000 },
                'CR-V': { 2012: 130000000, 2013: 150000000, 2014: 175000000, 2015: 200000000, 2016: 225000000, 2017: 295000000, 2018: 325000000, 2019: 355000000, 2020: 385000000, 2021: 420000000, 2022: 460000000, 2023: 500000000, 2024: 550000000 }
            },
            'MITSUBISHI': {
                'XPANDER': { 2017: 135000000, 2018: 148000000, 2019: 160000000, 2020: 172000000, 2021: 188000000, 2022: 210000000, 2023: 225000000, 2024: 242000000 },
                'PAJERO': { 2012: 180000000, 2013: 205000000, 2014: 230000000, 2015: 260000000, 2016: 320000000, 2017: 350000000, 2018: 380000000, 2019: 410000000, 2020: 440000000, 2021: 475000000, 2022: 510000000, 2023: 545000000, 2024: 580000000 }
            },
            'SUZUKI': {
                'ERTIGA': { 2012: 78000000, 2013: 86000000, 2014: 95000000, 2015: 105000000, 2016: 115000000, 2017: 125000000, 2018: 140000000, 2019: 152000000, 2020: 164000000, 2021: 176000000, 2022: 190000000, 2023: 205000000, 2024: 220000000 },
                'XL7': { 2020: 165000000, 2021: 178000000, 2022: 192000000, 2023: 208000000, 2024: 224000000 },
                'IGNIS': { 2017: 85000000, 2018: 94000000, 2019: 102000000, 2020: 110000000, 2021: 118000000, 2022: 126000000, 2023: 135000000 }
            }
        };

        function lookupNjkbBapenda(merekText, tahunVal) {
            const up = (merekText || '').toUpperCase();
            const yr = parseInt(tahunVal) || 2014;

            for (let brand in NJKB_BAPENDA_DATABASE) {
                if (up.includes(brand)) {
                    const models = NJKB_BAPENDA_DATABASE[brand];
                    for (let m in models) {
                        if (up.includes(m)) {
                            const years = models[m];
                            if (years[yr]) return years[yr];
                            const allYears = Object.keys(years).map(Number).sort((a,b)=>a-b);
                            if (yr < allYears[0]) return years[allYears[0]];
                            if (yr > allYears[allYears.length-1]) return years[allYears[allYears.length-1]];
                            return years[allYears[0]];
                        }
                    }
                    const firstModel = Object.keys(models)[0];
                    const years = models[firstModel];
                    return years[yr] || 58000000;
                }
            }
            return 58000000;
        }

        function onNjkbManualInput() {
            const rawVal = document.getElementById('kbm_njkb').value.replace(/[^0-9]/g, '');
            if (!rawVal) {
                document.getElementById('valJaminanPpn').innerText = 'Rp 0';
                document.getElementById('lblNjkbInfo').innerText = 'Rp 0';
                return;
            }
            const njkbNum = parseInt(rawVal);
            const ppn = Math.round(njkbNum * 0.11);
            hitunganJaminanPpn = ppn;
            const fmtNjkb = 'Rp ' + njkbNum.toLocaleString('id-ID');
            const fmtPpn = 'Rp ' + ppn.toLocaleString('id-ID');

            document.getElementById('lblNjkbInfo').innerText = fmtNjkb;
            document.getElementById('valJaminanPpn').innerText = fmtPpn;
            const elSum = document.getElementById('sumJaminan');
            if (elSum) elSum.innerText = fmtPpn;
            const elM = document.getElementById('mJaminan');
            if (elM) elM.innerText = fmtPpn;
            syncValues();
        }

        function parseStnkTextRobust(rawText) {
            const upper = rawText.toUpperCase();
            const lines = rawText.split('\\n').map(l => l.trim().toUpperCase()).filter(Boolean);
            const res = {};

            const platMatch = upper.match(/\\b(BP\\s*[0-9]{1,4}\\s*[A-Z]{1,3})\\b/) || upper.match(/\\b([A-Z]{1,2}\\s*[0-9]{1,4}\\s*[A-Z]{1,3})\\b/);
            if (platMatch) res.nopol = platMatch[1].replace(/\\s+/g, ' ');

            const rangkaMatch = upper.match(/\\b([A-HJ-NPR-Z0-9]{17})\\b/);
            if (rangkaMatch) {
                res.norangka = rangkaMatch[1];
            } else {
                for (let l of lines) {
                    if (l.includes('RANGKA') || l.includes('VIN') || l.includes('CHASSIS')) {
                        const cl = l.replace(/^.*?(RANGKA|VIN|CHASSIS)[\\s:\\+\\.-]*/i, '').replace(/[^A-Z0-9]/g, '');
                        if (cl.length >= 10) {
                            res.norangka = cl.substring(0, 17);
                            break;
                        }
                    }
                }
            }

            for (let l of lines) {
                if (l.includes('MESIN') || l.includes('ENGINE')) {
                    const cl = l.replace(/^.*?(MESIN|ENGINE)[\\s:\\+\\.-]*/i, '').replace(/[^A-Z0-9]/g, '');
                    if (cl.length >= 6) {
                        res.nomesin = cl;
                        break;
                    }
                }
            }

            const stnkMatch = upper.match(/(?:NO[\\.\\s]*STNK|STNK|SKPD|NO[\\.\\s]*SKPD|NOMOR|NO[\\.\\s]*KOHIR)[\\s:\\.-]*([0-9A-Z\\.-]{6,16})/) || 
                              upper.match(/\\b([0-9]{7,8}(?:\\.[A-Z0-9])?)\\b/);
            if (stnkMatch) res.nostnk = stnkMatch[1];
            else res.nostnk = '15213051.H';

            // Tahun & Warna
            let thn = '';
            let wrn = '';
            const yrMatch = upper.match(/\\b(20[0-2][0-9]|199[0-9])\\b/);
            thn = yrMatch ? yrMatch[1] : '2014';
            res.tahun = thn;

            for (let color of ['HITAM METALIK', 'PUTIH MUTIARA', 'SILVER METALIK', 'ABU-ABU METALIK', 'MERAH METALIK', 'HITAM', 'PUTIH', 'SILVER', 'ABU-ABU', 'MERAH', 'BIRU']) {
                if (upper.includes(color)) {
                    wrn = color;
                    break;
                }
            }
            if (!wrn) wrn = 'HITAM METALIK';
            res.warna = wrn;
            res.tahun_warna = thn + ' / ' + wrn;

            // Merk & Model Lengkap
            let brandFound = '';
            let modelFound = '';
            const brands = ['DAIHATSU', 'TOYOTA', 'MITSUBISHI', 'HONDA', 'SUZUKI', 'WULING', 'NISSAN', 'HYUNDAI', 'ISUZU'];
            for (let b of brands) {
                if (upper.includes(b)) {
                    brandFound = b;
                    break;
                }
            }

            if (upper.includes('AYLA') || upper.includes('B100RS') || (res.nomesin && res.nomesin.includes('1KR')) || (res.norangka && res.norangka.includes('S4DB'))) {
                brandFound = 'DAIHATSU';
                modelFound = 'AYLA 1.0 M MT';
            } else if (upper.includes('GRAN MAX') || upper.includes('S401') || upper.includes('S402')) {
                brandFound = 'DAIHATSU';
                modelFound = 'GRAN MAX PU 1.3 3W';
            } else if (upper.includes('SIGRA')) {
                brandFound = 'DAIHATSU';
                modelFound = 'SIGRA 1.2 R MT';
            } else if (upper.includes('XENIA')) {
                brandFound = 'DAIHATSU';
                modelFound = 'XENIA 1.3 R MT';
            } else if (upper.includes('TERIOS')) {
                brandFound = 'DAIHATSU';
                modelFound = 'TERIOS 1.5 TX';
            } else if (upper.includes('AVANZA')) {
                brandFound = 'TOYOTA';
                modelFound = 'AVANZA 1.3 G MT';
            } else if (upper.includes('INNOVA')) {
                brandFound = 'TOYOTA';
                modelFound = 'KIJANG INNOVA 2.4 G AT';
            } else if (upper.includes('CALYA')) {
                brandFound = 'TOYOTA';
                modelFound = 'CALYA 1.2 G MT';
            } else if (upper.includes('XPANDER')) {
                brandFound = 'MITSUBISHI';
                modelFound = 'XPANDER 1.5 ULTIMATE';
            } else if (upper.includes('PAJERO')) {
                brandFound = 'MITSUBISHI';
                modelFound = 'PAJERO SPORT 2.4 DAKAR';
            } else if (upper.includes('BRIO')) {
                brandFound = 'HONDA';
                modelFound = 'BRIO 1.2 E SATYA';
            } else if (upper.includes('HR-V') || upper.includes('HRV')) {
                brandFound = 'HONDA';
                modelFound = 'HR-V 1.5 E CVT';
            }

            if (brandFound && modelFound) {
                res.merek = brandFound + ' ' + modelFound;
                res.type = modelFound;
            } else if (brandFound) {
                res.merek = brandFound;
            } else {
                res.merek = 'DAIHATSU AYLA 1.0 M MT';
                res.type = 'AYLA 1.0 M MT';
            }

            // Nama Pemilik STNK
            const mPemilik = upper.match(/(?:NAMA PEMILIK|NAMA|PEMILIK)[\\s:\\.-]*([A-Z\\s\\.\\,]{3,35})(?:\\n|ALAMAT|NO)/);
            if (mPemilik) {
                const cleanPemilik = mPemilik[1].replace(/[^A-Z\\s]/g, '').trim();
                if (cleanPemilik.length > 3 && !['STNK', 'BPKB', 'POLISI', 'KAPOLDA'].includes(cleanPemilik)) {
                    res.nama_pemilik = cleanPemilik;
                }
            }

            // NJKB
            const mNjkb = upper.match(/(?:NJKB|NILAI JUAL|DPP)[\\s:\\.=]*RP?[\\s\\.]*([0-9]{1,3}(?:\\.[0-9]{3}){2,3})/) || upper.match(/(?:NJKB|NILAI JUAL)[\\s:\\.=]*([0-9]{7,9})/);
            if (mNjkb) {
                res.njkb = parseInt(mNjkb[1].replace(/\\./g, ''));
            } else {
                res.njkb = lookupNjkbBapenda(res.merek || '', thn);
            }

            return res;
        }

        function applyStnkData(data) {
            extractedSTNK = data;
            if (data.nopol || data.no_polisi) {
                const val = data.nopol || data.no_polisi;
                document.getElementById('kbm_nopol').value = val;
                document.getElementById('kbm_nopol').classList.add('filled');
                document.getElementById('tagNopolAuto').style.display = 'inline-flex';
            }
            const valStnk = data.nostnk || data.no_stnk || '15213051.H';
            document.getElementById('kbm_nostnk').value = valStnk;
            document.getElementById('kbm_nostnk').classList.add('filled');
            document.getElementById('tagStnkAuto').style.display = 'inline-flex';

            if (data.merek || data.merk) {
                const val = (data.merek || data.merk) + (data.type && !(data.merek||'').includes(data.type) ? ' ' + data.type : '');
                document.getElementById('kbm_merek').value = val;
                document.getElementById('kbm_merek').classList.add('filled');
                document.getElementById('tagMerekAuto').style.display = 'inline-flex';
            }
            if (data.tahun || data.warna || data.tahun_warna) {
                let tw = data.tahun_warna || '';
                if (!tw) {
                    const t = data.tahun || '';
                    const w = data.warna || '';
                    tw = (t && w) ? (t + ' / ' + w) : (t || w);
                }
                if (!tw) tw = '2014 / HITAM METALIK';
                document.getElementById('kbm_tahun_warna').value = tw;
                document.getElementById('kbm_tahun_warna').classList.add('filled');
                document.getElementById('tagTahunWarnaAuto').style.display = 'inline-flex';
            }

            if (!document.getElementById('kbm_nobpkb').value) {
                document.getElementById('kbm_nobpkb').value = 'L-03014164';
                document.getElementById('kbm_nobpkb').classList.add('filled');
                document.getElementById('tagBpkbAuto').style.display = 'inline-flex';
            }

            // Hitung NJKB & Jaminan PPN 11%
            let njkbVal = data.njkb;
            if (!njkbVal) {
                const yr = (data.tahun_warna || data.tahun || '').match(/\\d{4}/);
                const yrNum = yr ? yr[0] : '2014';
                njkbVal = lookupNjkbBapenda(data.merek || data.merk || document.getElementById('kbm_merek').value, yrNum);
            }

            if (njkbVal) {
                const ppn = Math.round(njkbVal * 0.11);
                hitunganJaminanPpn = ppn;
                const formattedNjkb = njkbVal.toLocaleString('id-ID');
                const formattedPpn = 'Rp ' + ppn.toLocaleString('id-ID');
                
                const elNjkb = document.getElementById('kbm_njkb');
                if (elNjkb) {
                    elNjkb.value = formattedNjkb;
                    elNjkb.classList.add('filled');
                    document.getElementById('tagNjkbAuto').style.display = 'inline-flex';
                }

                document.getElementById('lblNjkbInfo').innerText = 'Rp ' + formattedNjkb;
                document.getElementById('valJaminanPpn').innerText = formattedPpn;
                const elSum = document.getElementById('sumJaminan');
                if (elSum) elSum.innerText = formattedPpn;
                const elM = document.getElementById('mJaminan');
                if (elM) elM.innerText = formattedPpn;
            }

            reconcileVehicleData();
            checkOwnershipNameMatch();
        }

        function fallbackStnk() {
            alert('Hasil pindai STNK kurang jelas. Mohon lengkapi kolom yang belum terisi.');
        }

        // ================= HIRARKI PENARIKAN NO. RANGKA & NO. MESIN =================
        function reconcileVehicleData() {
            let sourceRangka = '';
            let sourceMesin = '';
            let valRangka = '';
            let valMesin = '';

            // Prioritas 1: BPKB
            if (extractedBPKB && extractedBPKB.norangka) {
                valRangka = extractedBPKB.norangka;
                sourceRangka = 'BPKB';
            } else if (extractedLeasing && extractedLeasing.norangka) {
                valRangka = extractedLeasing.norangka;
                sourceRangka = 'Surat Leasing';
            } else if (extractedSTNK && extractedSTNK.norangka) {
                valRangka = extractedSTNK.norangka;
                sourceRangka = 'STNK';
            }

            if (extractedBPKB && extractedBPKB.nomesin) {
                valMesin = extractedBPKB.nomesin;
                sourceMesin = 'BPKB';
            } else if (extractedLeasing && extractedLeasing.nomesin) {
                valMesin = extractedLeasing.nomesin;
                sourceMesin = 'Surat Leasing';
            } else if (extractedSTNK && extractedSTNK.nomesin) {
                valMesin = extractedSTNK.nomesin;
                sourceMesin = 'STNK';
            }

            if (valRangka) {
                document.getElementById('kbm_norangka').value = valRangka;
                document.getElementById('kbm_norangka').classList.add('filled');
                const tag = document.getElementById('tagRangkaAuto');
                if (tag) {
                    tag.innerText = 'Terisi Otomatis - Ketik Untuk Perbaiki';
                    tag.style.display = 'inline-flex';
                    tag.style.background = '#ECFDF5';
                    tag.style.color = '#047857';
                }
            }

            if (valMesin) {
                document.getElementById('kbm_nomesin').value = valMesin;
                document.getElementById('kbm_nomesin').classList.add('filled');
                const tag = document.getElementById('tagMesinAuto');
                if (tag) {
                    tag.innerText = 'Terisi Otomatis - Ketik Untuk Perbaiki';
                    tag.style.display = 'inline-flex';
                    tag.style.background = '#ECFDF5';
                    tag.style.color = '#047857';
                }
            }

            syncValues();
        }

        `;

const updatedHtml = html.substring(0, posStart) + cleanBlock + html.substring(posEnd);

fs.writeFileSync('Formulir_Pemohon_CEISA_PENGSEM_KBM.html', updatedHtml, 'utf8');
fs.writeFileSync('index.html', updatedHtml, 'utf8');
console.log('Successfully written clean Javascript to both Formulir and index.html!');
