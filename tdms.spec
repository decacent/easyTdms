# -*- mode: python -*-

block_cipher = None


a = Analysis(['tdms.py'],
             pathex=['E:\\Develop\\Python\\EasyTDMS'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='tdms',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='ui.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='tdms')
