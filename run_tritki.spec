# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['run_tritki.py'],
             pathex=['C:\\devel\\tritki'],
             binaries=[],
             datas=[
                 ('tritki\\gui\\mainwindow.ui', 'tritki\\gui'),
                 ('tritki\\templates\\article.html', 'tritki\\templates')
             ],
             hiddenimports=['tritki.gui.spelltextedit'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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
          name='run_tritki',
          debug=False,
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
