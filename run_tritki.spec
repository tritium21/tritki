# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['run_tritki.py'],
             pathex=['C:\\devel\\tritki'],
             binaries=[],
             datas=[
                 ('tritki\\data\\__init__.py', 'tritki\\data'),
                 ('tritki\\data\\mainwindow.ui', 'tritki\\data'),
                 ('tritki\\data\\words.txt', 'tritki\\data'),
                 ('tritki\\data\\templates\\', 'tritki\\data\\templates')
             ],
             hiddenimports=['tritki.gui.spelltextedit'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[
                 'PyQt5.QtSerialPort',
                 'PyQt5.QtBluetooth',
                 'PyQt5.QtDbus',
                 'PyQt5.QtDesigner',
                 'PyQt5.QtHelp',
                 'PyQt5.QtLocation',
                 'PyQt5.QtMultimedia',
                 'PyQt5.QtMultimediaWidgets',
                 'PyQt5.QtNetwork',
                 'PyQt5.QtNetworkAuth',
                 'PyQt5.QtNfc',
                 'PyQt5.QtOpenGL',
                 'PyQt5.QtQml',
                 'PyQt5.QtQuick',
                 'PyQt5.QtQuickWidgets',
                 'PyQt5.QtSensors',
                 #'PyQt5.QtSql', # rewrite forthcoming to remove this
                 'PyQt5.QtSvg',
                 'PyQt5.QtTest',
                 'PyQt5.QtWebChannel',
                 'PyQt5.QtWebSockets',
             ],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='tritki',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='tritki')
