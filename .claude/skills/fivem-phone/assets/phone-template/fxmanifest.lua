fx_version 'cerulean'
game 'gta5'
lua54 'yes'

name 'phone-template'
description 'FiveM phone template: frame, foldable inner screen, Messages, Wallet, Settings'
version '1.1.0'

shared_scripts { '@ox_lib/init.lua', 'config.lua' }
client_script 'client.lua'
server_script 'server.lua'

ui_page 'web/index.html'
files {
    'web/index.html',
    'web/style.css',
    'web/app.js',
    'web/icons.js',
    'web/fonts/*.woff2',
}

dependencies { 'ox_lib' }
