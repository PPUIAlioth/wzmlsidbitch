from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from functools import partial
from collections import OrderedDict
from time import time, sleep
from os import remove, rename, path as ospath, environ
from subprocess import run as srun, Popen
from dotenv import load_dotenv
from bot import config_dict, dispatcher, user_data, DATABASE_URL, tgBotMaxFileSize, DRIVES_IDS, DRIVES_NAMES, INDEX_URLS, aria2, GLOBAL_EXTENSION_FILTER, LOGGER, status_reply_dict_lock, Interval, aria2_options, aria2c_global, download_dict, qbit_options, get_client
from bot.helper.telegram_helper.message_utils import sendFile, sendMarkup, editMessage, update_all_messages
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.ext_utils.bot_utils import new_thread, setInterval
from bot.helper.ext_utils.db_handler import DbManger
from bot.modules.search import initiate_search_tools

START = 0
STATE = 'view'
handler_dict = {}
default_values = {'AUTO_DELETE_MESSAGE_DURATION': 30,
                  'AUTO_DELETE_UPLOAD_MESSAGE_DURATION': -1,
                  'BOT_PM': False,
                  'FORCE_BOT_PM': False,
                  'UPDATE_PACKAGES': 'False',
                  'UPSTREAM_BRANCH': 'master',
                  'UPSTREAM_REPO': 'https://github.com/weebzone/WZML',
                  'STATUS_UPDATE_INTERVAL': 10,
                  'DOWNLOAD_DIR': '/usr/src/app/downloads/',
                  'TIME_GAP': -1,
                  'TG_SPLIT_SIZE': tgBotMaxFileSize,
                  'TGH_THUMB': 'https://te.legra.ph/file/3325f4053e8d68eab07b5.jpg',
                  'START_BTN1_NAME': 'Master',
                  'START_BTN1_URL': 'https://t.me/krn_adhikari',
                  'START_BTN2_NAME': 'Support Group',
                  'START_BTN2_URL': 'https://t.me/WeebZone_updates',
                  'AUTHOR_NAME': 'WZML',
                  'AUTHOR_URL': 'https://t.me/WeebZone_updates',
                  'TITLE_NAME': 'WeebZone',
                  'GD_INFO': 'Uploaded by WeebZone Mirror Bot',
                  'CREDIT_NAME': 'WeebZone',
                  'NAME_FONT': 'code',
                  'CAPTION_FONT': 'code',
                  'FINISHED_PROGRESS_STR': '█',
                  'UN_FINISHED_PROGRESS_STR': '▒',
                  'MULTI_WORKING_PROGRESS_STR': '▁ ▂ ▃ ▄ ▅ ▆ ▇'.split(' '),
                  'CHANNEL_USERNAME': 'WeebZone_updates',
                  'FSUB_CHANNEL_ID': '-1001512307861',
                  'IMAGE_URL': 'https://graph.org/file/6b22ef7b8a733c5131d3f.jpg',
                  'TIMEZONE': 'Asia/Kolkata',
                  'SEARCH_LIMIT': 0,
                  'PICS': 'https://te.legra.ph/file/9634110b5c61bb9ddf7ab.jpg https://te.legra.ph/file/4ecdeb0e51d1ae8c67e49.jpg https://te.legra.ph/file/a8a51e4e523404baba293.jpg https://te.legra.ph/file/6dcad49b1e3e8dfdf9998.jpg https://te.legra.ph/file/0f8ca487996c95c93ee32.jpg https://te.legra.ph/file/92b4d657954a988491cb1.jpg https://te.legra.ph/file/5878ac378467c815d98cb.jpg https://te.legra.ph/file/418e85216bf27a96af246.jpg https://te.legra.ph/file/5a54380aa3aa0942beeaf.jpg https://te.legra.ph/file/f17945c6363e8ee2fcaaf.png https://te.legra.ph/file/2088a2622dd36049d5cde.jpg https://te.legra.ph/file/04900e542473adfcaaced.jpg https://te.legra.ph/file/73413c5ad18cad4a55018.jpg https://te.legra.ph/file/78fb58b1b85ed80b8ecbf.jpg https://te.legra.ph/file/4fb19610d38eae5701f50.jpg https://te.legra.ph/file/f49317cb5b5d6e623db1a.jpg https://te.legra.ph/file/e1b18b011aeaf5e254143.jpg https://te.legra.ph/file/eaa728c45fefbca806143.jpg https://te.legra.ph/file/131ff89921a0b28bfc473.jpg https://te.legra.ph/file/f56dff8b2bb9183b46dbf.jpg https://te.legra.ph/file/b23eb69a8e21504d90a04.jpg https://te.legra.ph/file/71d3f97949fb72ccad27c.jpg https://te.legra.ph/file/7a080d1cad32296b54da9.jpg https://te.legra.ph/file/2e1e900875c0916650c30.jpg https://te.legra.ph/file/9d885ecdf98f01d3e711f.jpg https://te.legra.ph/file/55749551f3451037cb012.jpg https://te.legra.ph/file/509cf0449af9290c0cf3b.jpg https://te.legra.ph/file/c0db3dd8dab420a7ae4c4.jpg https://te.legra.ph/file/191f81ccd1ac889304f23.jpg https://te.legra.ph/file/078562c7e4cfd78fd1d69.jpg https://te.legra.ph/file/cd4fd4ee6b25b964a44d0.jpg https://te.legra.ph/file/bed359bc307fef90acbb6.jpg https://te.legra.ph/file/6f0ece88bc6141affd7db.jpg https://te.legra.ph/file/7301f4a7009ad46700e88.jpg https://te.legra.ph/file/8557fb115268c3c7addb5.jpg https://te.legra.ph/file/41bfcb2f8eed2a1b8d657.jpg https://te.legra.ph/file/843d5571f1dea128d964d.jpg https://te.legra.ph/file/e659cdf47625fd1865aaf.jpg https://te.legra.ph/file/fcffd5d12d1b4f7e61ef6.jpg https://te.legra.ph/file/478e9f18622a1a04b3f4a.jpg https://te.legra.ph/file/a6ea04b4d8a8ff38dd6ae.jpg https://te.legra.ph/file/0417b217a8b1c9f5bd4b8.jpg https://te.legra.ph/file/298048a05a16919f65f59.jpg https://te.legra.ph/file/38a32756968175cff0877.jpg https://te.legra.ph/file/098b7bc300b305e3be48c.jpg https://te.legra.ph/file/dc647090401abacbbee77.jpg https://te.legra.ph/file/93d3c8598632e103e137f.jpg https://te.legra.ph/file/f7ad8df55ed09df7a28fc.jpg https://te.legra.ph/file/1e1efd136e529ab25c33f.jpg https://te.legra.ph/file/6dbf9378cd63a4647d85e.jpg https://te.legra.ph/file/b96ccb98c547458be4fa0.jpg https://te.legra.ph/file/ed3b81fa9e8c92093d756.jpg https://te.legra.ph/file/133f9fef01c468127d203.jpg https://te.legra.ph/file/3e8f30b9620d5c28b6ccd.jpg https://te.legra.ph/file/cc5191fbe50650dce0c34.jpg https://te.legra.ph/file/6e7a5e8962aa72b4d87e8.jpg https://te.legra.ph/file/e0fe314fda8ac24aa18bb.jpg https://te.legra.ph/file/319f1dbb57f7d36188d0b.jpg https://te.legra.ph/file/3919b9309e67d99351703.jpg https://te.legra.ph/file/085e0396c0fe8d176670d.jpg https://te.legra.ph/file/26a64b45fe96174e6648d.jpg https://te.legra.ph/file/1ed3d4434c52a0d204e39.jpg https://te.legra.ph/file/8c85530836df55fa9c9a2.jpg https://te.legra.ph/file/69f55a066b27008179e26.jpg https://te.legra.ph/file/b71f10e5192790e2c7c62.jpg https://te.legra.ph/file/5c6b5dc4c776f9271cafc.jpg https://te.legra.ph/file/585c621c1053cd42e3ce9.jpg https://te.legra.ph/file/308c5b590e738254e4961.jpg https://te.legra.ph/file/3dc0a0f63339105029ba6.jpg https://te.legra.ph/file/2028e909b2460438c49d6.jpg https://te.legra.ph/file/321d99356bc110aa295d8.jpg https://te.legra.ph/file/948fed8ca4a2fcb43880e.jpg https://te.legra.ph/file/3bb54b230792bea0a43d4.jpg https://te.legra.ph/file/3f0a4f4b9194b47d24c7e.jpg https://te.legra.ph/file/cf77bbbdef3ccf93ccb21.jpg https://te.legra.ph/file/7d3fd73fdcdb226ecb0fa.jpg https://te.legra.ph/file/2e19e4c9a195c0b628943.jpg https://te.legra.ph/file/9a4aa4438f01d1280c1ad.jpg https://te.legra.ph/file/9362ac940c9138a2a4da8.jpg https://te.legra.ph/file/f3ccb2ecfc353b86a3c22.jpg https://te.legra.ph/file/6a04c30d82c3534e0795d.jpg https://te.legra.ph/file/5c349b2ac0096077631ef.jpg https://te.legra.ph/file/cd25b880b8c4901b014f7.jpg https://te.legra.ph/file/ddc8f0e7f8448251b8d01.jpg https://te.legra.ph/file/2562a6f776b61e52a24e6.jpg https://te.legra.ph/file/094bd0e1da68f32507f02.jpg https://te.legra.ph/file/ed6b0e2074c7cd5bbbf50.jpg https://te.legra.ph/file/00f15e3bd277e973fbbab.jpg https://te.legra.ph/file/8304f2ce715623e1ebc38.jpg https://te.legra.ph/file/58aee704fd7259bce3097.jpg https://te.legra.ph/file/180571ad231488a9a6cd0.jpg https://te.legra.ph/file/e77381d657d343633d5e9.jpg https://te.legra.ph/file/ac9ec8e0ec8262944c3b5.jpg https://te.legra.ph/file/aebf87a19ee64c5f4c21c.jpg https://te.legra.ph/file/5c95bafe1452724830aa3.jpg https://te.legra.ph/file/b06cbb61ec28d1c9104e3.jpg https://te.legra.ph/file/871bb463f280f1ba83079.jpg https://te.legra.ph/file/29e1a616fe5e751b59275.jpg https://te.legra.ph/file/4ab90ff2750637990ac52.jpg https://te.legra.ph/file/dffe0a1f7641cd60021f2.jpg https://te.legra.ph/file/4fc65510ca333a596b6ba.jpg https://te.legra.ph/file/22f41301ebd438541c094.jpg https://te.legra.ph/file/12213978570b47f2bd601.jpg https://te.legra.ph/file/e5f449eb76ee43c7891ac.jpg https://te.legra.ph/file/0e26572008c29ff828fac.jpg https://te.legra.ph/file/4d083d0277b7d218a58db.jpg https://te.legra.ph/file/1b35e1f9ee27ebd798174.jpg https://te.legra.ph/file/34282b31030b477ca4070.jpg https://te.legra.ph/file/e7338883ffcac6c9d3ed2.jpg https://te.legra.ph/file/dc2d0b111b795c67983de.jpg https://te.legra.ph/file/17e0ebe6eb0650025dce9.jpg https://te.legra.ph/file/752f0ad71a6dae84a11b5.jpg https://te.legra.ph/file/b5d34787db4872b00d66a.jpg https://te.legra.ph/file/7a5d7e79dee6cf4d6c7d9.jpg https://te.legra.ph/file/062d22ef1c7670eca8e44.jpg https://te.legra.ph/file/da6e1f4174891a3465792.jpg https://te.legra.ph/file/ab306bb21c7d647d524db.jpg https://te.legra.ph/file/06e80daa7fe8eb27590f0.jpg https://te.legra.ph/file/e2f7c54eb81eeeada29e2.jpg https://te.legra.ph/file/68276c0b72f5343698066.jpg https://te.legra.ph/file/cd8ca3968a529ee8551b0.jpg https://te.legra.ph/file/b4911a4cc0ebb5889c5e2.jpg https://te.legra.ph/file/a5e168f9568674aace157.jpg https://te.legra.ph/file/d73b2fbbd0590c0e73c28.jpg https://te.legra.ph/file/2d55ca896d2946b4e1f97.jpg https://te.legra.ph/file/8fe5930674841414c17f7.jpg https://te.legra.ph/file/17c12c276fc384f78a590.jpg https://te.legra.ph/file/e4037aa3bfdbe8daee251.jpg https://te.legra.ph/file/f8461b99fec99d28bd239.jpg https://te.legra.ph/file/56215f28ffe66df6fdb7a.jpg https://te.legra.ph/file/f8653e272ce2f03694de8.jpg https://te.legra.ph/file/81daa1bdcc0a61b7fca9a.jpg https://te.legra.ph/file/6aedb95949284037f08a2.jpg https://te.legra.ph/file/82067b29912b952c30aba.jpg https://te.legra.ph/file/939aea49076bbc18bda0d.jpg https://te.legra.ph/file/61b41e790bdf590e9c9c6.jpg https://te.legra.ph/file/0e7b23bf26dd95257738c.jpg https://te.legra.ph/file/f2009692f60f5bf875b34.jpg https://te.legra.ph/file/31447154547c2cdeed7b3.jpg https://te.legra.ph/file/492f768e169e5f48bf413.jpg https://te.legra.ph/file/318ea7162e91a7ceded97.jpg https://te.legra.ph/file/b5127ae0936e106769387.jpg https://te.legra.ph/file/196d4a0233e8a733f22f7.jpg https://te.legra.ph/file/f281ea6ef6f0b7979658f.jpg https://te.legra.ph/file/d73d283b9e85524be5335.jpg https://te.legra.ph/file/072aca725ddc18849baa7.jpg https://te.legra.ph/file/904f1658989ca733367e5.jpg https://te.legra.ph/file/4ba42d19696b98208edba.jpg https://te.legra.ph/file/5ebc03dfad23506f7b7f4.jpg https://te.legra.ph/file/be2f61287d9cabd81bd4e.jpg https://te.legra.ph/file/59adc00037e24052aabf7.jpg https://te.legra.ph/file/4c8acecf2d9aaf712a50d.jpg https://te.legra.ph/file/69cc5d2aea4ba4f607742.jpg https://te.legra.ph/file/8fbf97ecc676c89da560b.jpg https://te.legra.ph/file/21e158e3a9dfcc2279ea7.jpg https://te.legra.ph/file/258781fc36e05e5d92760.jpg https://te.legra.ph/file/a7165cac3ce0cce0e3dbe.jpg https://te.legra.ph/file/101c572f328e1255a5b0d.jpg https://te.legra.ph/file/bdb1c02baed3b163fd5f2.jpg https://te.legra.ph/file/ee53442631fa2fec4e458.jpg https://te.legra.ph/file/aab04cc40d5fb0cce7935.jpg https://te.legra.ph/file/6a19a766516ef11f4511f.jpg https://te.legra.ph/file/66acdbe7886734c305048.jpg https://te.legra.ph/file/7e7db109364950dfc8a47.jpg https://te.legra.ph/file/f7375a5d978d8126a91a4.jpg https://te.legra.ph/file/64b473018b29d7bbf3017.jpg https://te.legra.ph/file/69afc58f859926d5697c4.jpg https://te.legra.ph/file/efa17eff5ccf220bad612.jpg https://te.legra.ph/file/fd1a34f9edd52cfe2aca3.jpg https://te.legra.ph/file/e0b1319da0da69e8e863e.jpg https://te.legra.ph/file/e0b1319da0da69e8e863e.jpg https://te.legra.ph/file/d24b2e79efcc8817c2dcd.jpg https://te.legra.ph/file/8993a0bef41c656e96e6c.jpg https://te.legra.ph/file/d0c4f6fa219f08bd5cc2d.jpg https://te.legra.ph/file/d78ae8d546fccaaf78a08.jpg https://te.legra.ph/file/92b26e65001ad8ae21c06.jpg https://te.legra.ph/file/0dcc8a15b4ebc77adf1f0.jpg https://te.legra.ph/file/bee81f2c7842786deb81c.jpg https://te.legra.ph/file/8cc765fa580618235a785.jpg https://te.legra.ph/file/03784725af90f59d1b67c.jpg https://te.legra.ph/file/ce99d9460bdc7222c79d9.jpg https://te.legra.ph/file/ca3c4894d07acd097a4a4.jpg https://te.legra.ph/file/d415dc71e9ae136b15b14.jpg https://te.legra.ph/file/a61b19bfdab73b6d4c5a9.jpg https://te.legra.ph/file/0789791dcd77b2cc27b94.jpg https://te.legra.ph/file/5e39587c763cbd7e0e19b.jpg https://te.legra.ph/file/0378df72b2e533ee6fb7e.jpg https://te.legra.ph/file/a2501ef579ccf0a1db7e1.jpg https://te.legra.ph/file/5fa8c9d49e5aedd110637.jpg https://te.legra.ph/file/3cb1961dfc496f384e32c.jpg https://te.legra.ph/file/4282669142d197d2953ed.jpg https://te.legra.ph/file/ca00100c62ef067f12630.jpg https://te.legra.ph/file/5f40400abd878002a11d1.jpg https://te.legra.ph/file/5ca6b07f72403ba6a08be.jpg https://te.legra.ph/file/9d286e77408cce6eeac54.jpg https://te.legra.ph/file/43655497d413f72c9c740.jpg https://te.legra.ph/file/85cfab84b8b40ba1937c2.jpg https://te.legra.ph/file/13563085e249944e12b16.jpg https://te.legra.ph/file/4754309d771d6dc9a0a25.jpg https://te.legra.ph/file/e2b48914c883defdb7f35.jpg https://te.legra.ph/file/03e536f26eed3b2ecff30.jpg https://te.legra.ph/file/25f9a032b49c3f7d30f46.jpg https://te.legra.ph/file/dfd0f4a5a1c9e4432e9c1.jpg https://te.legra.ph/file/a789d1d95a0bfe76415d1.jpg https://te.legra.ph/file/5d015bf58a9eaeeaabe52.jpg https://te.legra.ph/file/d46e7d0d891af0aee46c3.jpg https://te.legra.ph/file/2868b17638778883d9df4.jpg https://te.legra.ph/file/dbb8884d71346a41dfa3a.jpg https://te.legra.ph/file/1f34d3f6f640e359d2435.jpg https://te.legra.ph/file/54749c06785a18d48e8f6.jpg https://te.legra.ph/file/ca3f869660508678c8539.jpg https://te.legra.ph/file/dee0291bf8971698b7cf6.jpg https://te.legra.ph/file/41eaa387643d4b4f11dda.jpg https://te.legra.ph/file/9e49041707925335aa0be.jpg https://te.legra.ph/file/5dc0d9a1bbd2544db1958.jpg https://te.legra.ph/file/af518dedd71a581f19934.jpg https://te.legra.ph/file/ad2c09a52dbcdb98aa7b8.jpg https://te.legra.ph/file/5c5d81fd60c792f5a88e7.jpg https://te.legra.ph/file/5ad1fb0378c13d1337d93.jpg https://te.legra.ph/file/33a0f3ca714578a0c8ddf.jpg https://te.legra.ph/file/a231523fba13ef60d3fd8.jpg https://te.legra.ph/file/ad19692bcf75bb819ffa3.jpg https://te.legra.ph/file/8ce709d29687d42f0d89e.jpg https://te.legra.ph/file/0d4d8dfd1f4b385864cb7.jpg https://te.legra.ph/file/eeeebb1b83a2749253dec.jpg https://te.legra.ph/file/684f4080136bec512dfc3.jpg https://te.legra.ph/file/0f8e6f06d85a0f674eaef.jpg https://te.legra.ph/file/37bb8d7b39dd5b9bf1897.jpg https://te.legra.ph/file/83d619728687f5d2a96e0.jpg https://te.legra.ph/file/f18413dc0effa6ea939b2.jpg https://te.legra.ph/file/280d7a504dd8ad5c7c7d0.jpg https://te.legra.ph/file/52a308164b427fc39dadb.jpg https://te.legra.ph/file/48546f236941a193b0dba.jpg https://te.legra.ph/file/3681475324153ad0816d1.jpg https://te.legra.ph/file/6ee6f7d14263f9f931d68.jpg https://te.legra.ph/file/a02cf1c66b12100bef32f.jpg https://te.legra.ph/file/d526b09956c33fcffa5be.jpg https://te.legra.ph/file/b13223257b8b8754202c1.jpg https://te.legra.ph/file/1264bf1ec95565c8de6c7.jpg https://te.legra.ph/file/a7522b577cb66cf08416a.jpg https://te.legra.ph/file/051259502de0c753da77d.jpg https://te.legra.ph/file/27f1a9cd74a53314901a9.jpg https://te.legra.ph/file/d97dd51bff1c690dcf27a.jpg https://te.legra.ph/file/6b24f61fe17307112eca3.jpg https://te.legra.ph/file/8ceb38fc314dd99780028.jpg https://te.legra.ph/file/2d4f2c5737d08937e6a90.jpg https://te.legra.ph/file/e1f62f15e0a3bb694fef0.jpg https://te.legra.ph/file/01f448c3d855a2e3c1e0e.jpg https://te.legra.ph/file/acf0a65de329b5665d583.jpg https://te.legra.ph/file/d3d092e1a6f103980b428.jpg https://te.legra.ph/file/b1a802dc77a6491917a37.jpg https://te.legra.ph/file/33d092a2f534aedb920fb.jpg https://te.legra.ph/file/315c587b26561932090c1.jpg https://te.legra.ph/file/50ab3de095ee30e591a01.jpg https://te.legra.ph/file/ea6035bc74bd363a5eef1.jpg https://te.legra.ph/file/7907efb463110709db38e.jpg https://te.legra.ph/file/65f5affa1bf2748da8ea1.jpg https://te.legra.ph/file/83daff1d7fe1f02acc930.jpg https://te.legra.ph/file/2b03545eee69d30d38e7f.jpg https://te.legra.ph/file/e2f6071dc9bbe10d5669d.jpg https://te.legra.ph/file/923959fd8b84ef0d5e4eb.jpg https://te.legra.ph/file/ea3d22bab26ce85719697.jpg https://te.legra.ph/file/4a60f2f7d035aa6ffdcb2.jpg https://te.legra.ph/file/756e30f96fd4c73f118d3.jpg https://te.legra.ph/file/1c5347f2d1b78319e7f71.jpg https://te.legra.ph/file/ada65224e8606bea5064b.jpg https://te.legra.ph/file/f47a2aafb4a8e26be7f5b.jpg https://te.legra.ph/file/8f9871f7c17137bf586f5.jpg https://te.legra.ph/file/36e7741871d2383602691.jpg https://te.legra.ph/file/5f25dacf47dbee811f930.jpg https://te.legra.ph/file/c46d604ccaf49009230f8.jpg https://te.legra.ph/file/fd5ebfe5109968dc3eab7.jpg https://te.legra.ph/file/53bc849b26a533d4d06ef.jpg https://te.legra.ph/file/a2f8873e52c59406cb79a.jpg https://te.legra.ph/file/8fce7d928253e039f0256.jpg https://te.legra.ph/file/6f4ad2ff3fb6874c60426.jpg https://te.legra.ph/file/a7d7305adba136e498153.jpg https://te.legra.ph/file/8b3d2e79888cf08f9ceba.jpg https://te.legra.ph/file/f9907cd5703f0dee4887e.jpg https://te.legra.ph/file/dfcbb39d8ec32b418e632.jpg https://te.legra.ph/file/b70beeb32882b51ca1897.jpg https://te.legra.ph/file/398ab2b7e4db8805a28b1.jpg https://te.legra.ph/file/778111b45fdb62c2856e4.jpg https://te.legra.ph/file/f07ad10bcfa29d7fdded2.jpg https://te.legra.ph/file/751519d43b58fb92d2265.jpg https://te.legra.ph/file/80f211314a669a30748a0.jpg https://te.legra.ph/file/3cf90f6fa4d071516098c.jpg https://te.legra.ph/file/7d29fd1cd81031646d43e.jpg https://te.legra.ph/file/29f47b2eae7efcaf40d66.jpg https://te.legra.ph/file/3686499d38e4b51849bb2.jpg https://te.legra.ph/file/d2016da17cb683d234f09.jpg https://te.legra.ph/file/98560cb52ba46af870e88.jpg https://te.legra.ph/file/3654255f28907f2fb0760.jpg https://te.legra.ph/file/f28e5a5c8594a7cebe59f.jpg https://te.legra.ph/file/d9df8f1cf3f4fbc1f8748.jpg https://te.legra.ph/file/f15719d14fe523baf4d24.jpg https://te.legra.ph/file/54f868eedd08eeccca9c1.jpg https://te.legra.ph/file/576e8f45bb8aa3aa61808.jpg https://te.legra.ph/file/272b87e2a94ed01df4984.jpg https://te.legra.ph/file/21fe3381316b3ed1cf1d9.jpg https://te.legra.ph/file/6bab219270b76224c3134.jpg https://te.legra.ph/file/a8a8a0ddef58da63a7d1c.jpg https://te.legra.ph/file/61c6f3b2e4795252ee61b.jpg https://te.legra.ph/file/86be37c155af7f43046c5.jpg https://te.legra.ph/file/899671f1654c16123d1a3.jpg https://te.legra.ph/file/25f302a9821837fca316b.jpg https://te.legra.ph/file/d56dde8d7091de5294396.jpg https://te.legra.ph/file/32703e6a0411a1a66e26b.jpg https://te.legra.ph/file/2a7e0365edcdf53be126e.jpg https://te.legra.ph/file/0e158350820ded3483042.jpg https://te.legra.ph/file/1e97c28f96714440f203d.jpg https://te.legra.ph/file/359877e66c0bd2daf3690.jpg https://te.legra.ph/file/be2ed4c6edb32c40f7430.jpg https://te.legra.ph/file/8eb06b11098782e0ec02d.jpg https://te.legra.ph/file/e267c2ce5a83ca8582013.jpg https://te.legra.ph/file/1467d10394a2c5b37fb1e.jpg https://te.legra.ph/file/34edc5e4b0d5f88471802.jpg https://te.legra.ph/file/6146bfcd0824c5840b0a6.jpg https://te.legra.ph/file/53efbff22f959bcaaf346.jpg https://te.legra.ph/file/6b5569e343554bfeefd22.jpg https://te.legra.ph/file/bab4e72f6205f9487d388.jpg https://te.legra.ph/file/c46ba1bdec42bfaa92ad8.jpg https://te.legra.ph/file/5272127c0b71f4995776b.jpg https://te.legra.ph/file/bbbd8aec22759bad9a3f6.jpg https://te.legra.ph/file/29af84f9e35a66c3c6eb6.jpg https://te.legra.ph/file/80c5387217e3197df5db4.jpg https://te.legra.ph/file/e7beae627787f32ffd766.jpg https://te.legra.ph/file/02490f375941f2de60ca4.jpg https://te.legra.ph/file/e0010824292e8076ebd30.jpg https://te.legra.ph/file/7df281cab0c7718cd2aa2.jpg https://te.legra.ph/file/ec8a2f7a93e46bd9b1dc3.jpg https://te.legra.ph/file/91861c1ffc949c795a5e6.jpg https://te.legra.ph/file/d0c9c8de3f7c7e76c31d0.jpg https://te.legra.ph/file/da0bfad1eb28977f0e080.jpg https://te.legra.ph/file/c0b17aacc177c5cffe339.jpg https://te.legra.ph/file/6a98edbf4e93bb7b17fd9.jpg https://te.legra.ph/file/80577c108e853888a39ae.jpg https://te.legra.ph/file/7788bd503fecfd50b2629.jpg https://te.legra.ph/file/9e3f04ff5cab0730ef4c7.jpg https://te.legra.ph/file/c0fe82714030ac6d65baf.jpg https://te.legra.ph/file/3df693ca0a116a0c7a49d.jpg https://te.legra.ph/file/93b7f8d66992e00aa26b5.jpg https://te.legra.ph/file/ef58c1d87fcd876aa95b0.jpg https://te.legra.ph/file/c908bb4ddff5fb114ec69.jpg https://te.legra.ph/file/38795b6227480e4f1f26e.jpg https://te.legra.ph/file/048bd6a91fd2ebeacc613.jpg https://te.legra.ph/file/6c0a1510c02cae1dbf318.jpg https://te.legra.ph/file/8c76519f041a6f6ce7f48.jpg https://te.legra.ph/file/5acdac72223b74ca555f9.jpg https://te.legra.ph/file/8c00076b991116b2b34b2.jpg https://te.legra.ph/file/dac89b41e080cc3365b07.jpg https://te.legra.ph/file/c20bba7253f196fc92dee.jpg https://te.legra.ph/file/523de43ef71f948b1452a.jpg https://te.legra.ph/file/bbcca8b7d227f26350848.jpg https://te.legra.ph/file/4a7c4ae8d542879903f20.jpg https://te.legra.ph/file/932fce9b3cea37e287c09.jpg https://te.legra.ph/file/751f3679eaee4067c400e.jpg https://te.legra.ph/file/f03e1631f9d0bee5fe401.jpg https://te.legra.ph/file/568ff27dd8b856488543c.jpg https://te.legra.ph/file/69f314f53fc0a1df98215.jpg https://te.legra.ph/file/59041ea565add54a2521d.jpg https://te.legra.ph/file/dfa17deb59f5ddaaf1254.jpg https://te.legra.ph/file/3ce41fa95fc9cede1504a.jpg https://te.legra.ph/file/f9e8f3217fcb1dfb3860f.jpg https://te.legra.ph/file/30989be2fe3a91f866ac8.jpg https://te.legra.ph/file/c00a10144c74b4ab42efe.jpg https://te.legra.ph/file/ff957db794b053290c5ba.jpg https://te.legra.ph/file/51763ac5975fea9d04835.jpg https://te.legra.ph/file/eeebb63ca53ed97dae73e.jpg https://te.legra.ph/file/c672d8e781ccf0df997cc.jpg https://te.legra.ph/file/792444d41fa7e04aa6d83.jpg https://te.legra.ph/file/b69685662888e3f08ab31.jpg https://te.legra.ph/file/76bfec03b0a828b33bb2e.jpg https://te.legra.ph/file/e51291dd9ccd389e73e03.jpg https://te.legra.ph/file/01b0a4e18942506b284f0.jpg https://te.legra.ph/file/087571fa3feb20ace2b95.jpg https://te.legra.ph/file/94445ab2aa63b76294cd1.jpg https://te.legra.ph/file/e5b7c2f225a419abcf0c6.jpg https://te.legra.ph/file/b5258c2baf9b8387bf771.jpg https://te.legra.ph/file/cc2726d22b83ef9059fbb.jpg https://te.legra.ph/file/081612727844eb1eb8478.jpg https://te.legra.ph/file/19322c59a44b483fd8267.jpg https://te.legra.ph/file/93802c8fa4477de224efe.jpg https://te.legra.ph/file/62bf6fe34e96abb5e9a1b.jpg https://te.legra.ph/file/246576bd7fb3cfcae3898.jpg https://te.legra.ph/file/aecaff25606f2d194573e.jpg https://te.legra.ph/file/f4a4d930b06b9f15583c3.jpg https://te.legra.ph/file/767e478ccac9e9b519d22.jpg https://te.legra.ph/file/3a0ef51a9b54e074991b6.jpg https://te.legra.ph/file/85f12f34f5850145e8c91.jpg https://te.legra.ph/file/b48e6e1ff2eaf23187bb7.jpg https://te.legra.ph/file/51241712c81141ec7df1b.jpg https://te.legra.ph/file/c60c587dcc6e341909026.jpg https://te.legra.ph/file/7ee8f8212e00432c83742.jpg https://te.legra.ph/file/36f7b2b25839264cf0ad5.jpg https://te.legra.ph/file/7bdbc70bf12d2183795be.jpg https://te.legra.ph/file/3056dcc3345858bd2040f.jpg https://te.legra.ph/file/460315c2e5471b08df71a.jpg https://te.legra.ph/file/88178c9691b444d74a7ae.jpg https://te.legra.ph/file/e29ef81699bc806f7fb7b.jpg https://te.legra.ph/file/965e80ec2a5e82fdf9f01.jpg https://te.legra.ph/file/f4ee3a5a99bbfa4988d07.jpg https://te.legra.ph/file/7de31e255d3df328c3a7c.jpg https://te.legra.ph/file/1ab7ffe212f72df5a463f.jpg https://te.legra.ph/file/ddef96d1670dd0f1a5ae2.jpg https://te.legra.ph/file/08c5ff615e4d3a3dd5a78.jpg https://te.legra.ph/file/5d489a1410b9fb4ec7c8e.jpg https://te.legra.ph/file/218b1adbeaeff0aaf49af.jpg https://te.legra.ph/file/4fb2922fadeebe00234a5.jpg https://te.legra.ph/file/88d8e7254ebe9ad816580.jpg https://te.legra.ph/file/545f50d90d20ad097e87f.jpg https://te.legra.ph/file/fbbd38cc5d9fe6c504586.jpg https://te.legra.ph/file/562721cc54db1f43961cb.jpg https://te.legra.ph/file/3e79b47ba3243d3c483f7.jpg https://te.legra.ph/file/c3c05fec23f22f36dd024.jpg https://te.legra.ph/file/f95f08a99e38cdcea9235.jpg https://te.legra.ph/file/a988ecfae0cdbd8d591a1.jpg https://te.legra.ph/file/7fb0426e416f7ffb93b46.jpg https://te.legra.ph/file/b1c8f47f759f876caff9d.jpg https://te.legra.ph/file/11e0c24c82c6d0d513290.jpg https://te.legra.ph/file/ecbc3c88bb0c31d1c37dc.jpg https://te.legra.ph/file/d02f9f70efc8e3c255293.jpg https://te.legra.ph/file/757704e80d5b5747f3a0b.jpg https://te.legra.ph/file/3b857b65be63de3e15280.jpg https://te.legra.ph/file/ceedb60a3289aa22fac61.jpg https://te.legra.ph/file/74149831914023643fd6e.jpg https://te.legra.ph/file/a2af0a8d6490fc9e600a2.jpg https://te.legra.ph/file/be5460c1b02d01d47dc07.jpg https://te.legra.ph/file/565ddba95c4dfa87148b0.jpg https://te.legra.ph/file/df4888c40313f59320190.jpg https://te.legra.ph/file/9c4f105957009933cbd0e.jpg https://te.legra.ph/file/763b34664edf1be213e02.jpg https://te.legra.ph/file/95fd2733374df244cc4c7.jpg https://te.legra.ph/file/1f7cc3baba523cf4dc29f.jpg https://te.legra.ph/file/21fd6d1e5a557c352268d.jpg https://te.legra.ph/file/7925a45fc260dc2ff94c9.jpg https://te.legra.ph/file/d49c6c999094d0a95f40d.jpg https://te.legra.ph/file/68b3481d295d80226b5f6.jpg https://te.legra.ph/file/11fa05a4bbebf1fdbc3b8.jpg https://te.legra.ph/file/5670cffb4dcdcb5b0f258.jpg https://te.legra.ph/file/ccd47aaab12190e27f1cd.jpg https://te.legra.ph/file/79d54b11ea56a69a25331.jpg https://te.legra.ph/file/fe1b05f484049088fc754.jpg https://te.legra.ph/file/c5d34286ebcf1e5edc968.jpg https://te.legra.ph/file/c2e53102ce662c4393093.jpg https://te.legra.ph/file/40d97a4fcae39640f95c8.jpg https://te.legra.ph/file/5dfa17aa181b8c90c1995.jpg https://te.legra.ph/file/3dab05f690bb93e36197d.jpg https://te.legra.ph/file/684ad412595da8591c5fc.jpg https://te.legra.ph/file/f67c12ab4603bc0768a09.jpg https://te.legra.ph/file/ab8f5046c73addbf3751b.jpg https://te.legra.ph/file/b9bb2461747057eaae79d.jpg https://te.legra.ph/file/d577fffc9aadc0b947040.jpg https://te.legra.ph/file/b899c82d3a67c933f2537.jpg https://te.legra.ph/file/fd34c41aa8aae1ca04191.jpg https://te.legra.ph/file/8f323b7b1d21cd688b7f8.jpg https://te.legra.ph/file/4c16df3cd8a64efc86815.jpg https://te.legra.ph/file/8f3c5b00164fc5c039959.jpg https://te.legra.ph/file/6a37c8b5e17f5ab3f0e90.jpg https://te.legra.ph/file/c48fe89a5fa1d698f7b96.jpg https://te.legra.ph/file/dbbb5618f8a08ff5a11d2.jpg https://te.legra.ph/file/0db22c4ff91e1baa48d56.jpg https://te.legra.ph/file/e5b88916b8c877249e717.jpg https://te.legra.ph/file/426c012e40e311dd1ea46.jpg https://te.legra.ph/file/6ddc752fb3d40d69eb15b.jpg https://te.legra.ph/file/4b165ff9d57ef8ef319a6.jpg https://te.legra.ph/file/cb635ba8c6467ca53dd9a.jpg https://te.legra.ph/file/13236f72ad25e6d6d4a77.jpg https://te.legra.ph/file/1c0e0b145bbee4cc2f63d.jpg https://te.legra.ph/file/8ccec865268320c896883.jpg https://te.legra.ph/file/57da5df33b5652cd4dd38.jpg https://te.legra.ph/file/87f109041f1fd08369cb4.jpg https://te.legra.ph/file/bcfa37b36953f78f4b8b5.jpg https://te.legra.ph/file/6fc5060aaa9e5eea900ca.jpg https://te.legra.ph/file/e83c03f4d997db002700c.jpg https://te.legra.ph/file/84ff24d288cae4c3bc058.jpg https://te.legra.ph/file/a9dc01834357af5ea4b84.jpg https://te.legra.ph/file/5da3665ac13b8473182df.jpg https://te.legra.ph/file/b5d5937020b2796ba2b81.jpg https://te.legra.ph/file/49cd6d79a9c7a661670db.jpg https://te.legra.ph/file/46e624f77761effda75e7.jpg https://te.legra.ph/file/5d518115f7fcb8dfc8961.jpg https://te.legra.ph/file/6ad201227ea34f3ffbd99.jpg https://te.legra.ph/file/c381de8f433771db0c3b7.jpg https://te.legra.ph/file/c12bb0ea2689dfcdd1569.jpg https://te.legra.ph/file/5012bc14192694e46a277.jpg https://te.legra.ph/file/db0279985ac9917f6e877.jpg https://te.legra.ph/file/c497eff210ed3890da340.jpg https://te.legra.ph/file/ee13d80701c1b29a72e41.jpg https://te.legra.ph/file/f3c1e9f12f883eedcde0f.jpg https://te.legra.ph/file/fe163a1562f1c4d4ca8c6.jpg https://te.legra.ph/file/f707d6f7b8065851d1380.jpg https://te.legra.ph/file/d1470fee2ff0aef70451e.jpg https://te.legra.ph/file/17818fca8417f060c5d95.jpg https://te.legra.ph/file/de750f67082208e9921b9.jpg https://te.legra.ph/file/f6b2c2891c8f7cf860a55.jpg https://te.legra.ph/file/73bf9cabe62079f702e8d.jpg https://te.legra.ph/file/53881525bf15cea628404.jpg https://te.legra.ph/file/0d48837996369351695ab.jpg https://te.legra.ph/file/3267a235ba48247ef49fd.jpg https://te.legra.ph/file/a5a0d59c419908eb0f7a5.jpg https://te.legra.ph/file/3fb81e59d8d96a160b494.jpg https://te.legra.ph/file/7e0f5a7ad155e6ae4552b.jpg https://te.legra.ph/file/cc20020054535c6a8d916.jpg https://te.legra.ph/file/8f75272b67fb7f12c6f14.jpg https://te.legra.ph/file/9dc786e1093c58f1c0509.jpg https://te.legra.ph/file/e6b04becc00a63199d199.jpg https://te.legra.ph/file/61401a47f6f3d66927e2e.jpg https://te.legra.ph/file/d747ee494c99e8385edd2.jpg https://te.legra.ph/file/e84b1df4d3ff7cf12dbc5.jpg https://te.legra.ph/file/55a249baa77706d928d08.jpg https://te.legra.ph/file/58a2ee6f52022dd1f6a52.jpg https://te.legra.ph/file/c7979fe3e08830ec67f25.jpg https://te.legra.ph/file/8e1680b97c5630e9851a8.jpg https://te.legra.ph/file/2ad9f56051456d89c3cd4.jpg https://te.legra.ph/file/10db2101d79d12028aa77.jpg https://te.legra.ph/file/bdb05750bf6cc9e622395.jpg https://te.legra.ph/file/154d30194b22f7e74e7c4.jpg https://te.legra.ph/file/a58287f7effce61d70332.jpg https://te.legra.ph/file/e5b8f0ae53d6cba478859.jpg https://te.legra.ph/file/48f009e466d9e0bf79d38.jpg https://te.legra.ph/file/7367a77df653b79e2b53d.jpg https://te.legra.ph/file/d7122345d8d55355a437e.jpg https://te.legra.ph/file/cfc13a13205af24abb7fe.jpg https://te.legra.ph/file/4dd829ac315a92464989c.jpg https://te.legra.ph/file/1c302d4f1ee6e99025f7f.jpg https://te.legra.ph/file/9e28dfc57070f489549ec.jpg https://te.legra.ph/file/f41b1d34034dac64d2b94.jpg https://te.legra.ph/file/7208088dc0bd76f3ee590.jpg https://te.legra.ph/file/ca486c3e645461a5608c9.jpg https://te.legra.ph/file/52e899f5e0355aec347ad.jpg https://te.legra.ph/file/f484e8ce145fbc3f5ef6c.jpg https://te.legra.ph/file/0f23f8c12f97a5680cdd3.jpg https://te.legra.ph/file/f0fff85e4cebd6c903907.jpg https://te.legra.ph/file/e6cd572c39b7e64790592.jpg https://te.legra.ph/file/101b87ed4327a03350367.jpg https://te.legra.ph/file/706d262ab774a6d34e040.jpg https://te.legra.ph/file/530e4260d134a9d42db43.jpg https://te.legra.ph/file/bb0816b1a1f4e2a69019a.jpg https://te.legra.ph/file/d91f81a2d76df47d8d09b.jpg https://te.legra.ph/file/b6e3ddf871c40dae4fd24.jpg https://te.legra.ph/file/f3c4c60269f4de6227d50.jpg https://te.legra.ph/file/10d28139e9ca704e76d41.jpg https://te.legra.ph/file/0c955e967861e57a40cad.jpg https://te.legra.ph/file/f5b92811abf9501dceaa1.jpg https://te.legra.ph/file/e792a394bab86bd1340b4.jpg https://te.legra.ph/file/d368298d97cedd3af901b.jpg https://te.legra.ph/file/d3fcd7e53ced51e5188ff.jpg https://te.legra.ph/file/4fb9c1ccf458723c78848.jpg https://te.legra.ph/file/5394612ef45ca71e82f13.jpg https://te.legra.ph/file/46c67ab4e65af8122709d.jpg https://te.legra.ph/file/257475fca0bb5eb89a47e.jpg https://te.legra.ph/file/e956b389886b6d548cf64.jpg https://te.legra.ph/file/a6c99d343c44041d4647c.jpg https://te.legra.ph/file/9fe3e690a0b5f88c4cde6.jpg https://te.legra.ph/file/f035ac714e6a3b87998ad.jpg https://te.legra.ph/file/45bb21ecd7d72c51c5a9e.jpg https://te.legra.ph/file/e8da16d52cf38cd4b22d0.jpg https://te.legra.ph/file/96587811a5a6003a3e3ab.jpg https://te.legra.ph/file/51d6ad593529721c69044.jpg https://te.legra.ph/file/cbc5efc4494c4c02a3200.jpg https://te.legra.ph/file/0c5fd5fc9b653e4adec64.jpg https://te.legra.ph/file/17837ed5bec420ab62254.jpg https://te.legra.ph/file/95e52afb7812e653baa79.jpg https://te.legra.ph/file/1dcdbbb64347602a08cba.jpg https://te.legra.ph/file/01dc5ffecf7f3dfc59fcb.jpg https://te.legra.ph/file/1daed9bd8b07119710930.jpg https://te.legra.ph/file/e798320c41d52730ae9b5.jpg https://te.legra.ph/file/0fbc1c6d324ffeb2ff07e.jpg https://te.legra.ph/file/9afde938fc1570861b51b.jpg https://te.legra.ph/file/8aa69ae670c7acfdb955c.jpg https://te.legra.ph/file/b5fd89a0df3175177a042.jpg https://te.legra.ph/file/9dd8c979f2312987eb797.jpg https://te.legra.ph/file/6222f0a574a9dd54ee084.jpg https://te.legra.ph/file/351d2dd5fa41113973d2a.jpg https://te.legra.ph/file/4bf5ca79d6798dde81d6d.jpg https://te.legra.ph/file/ced015fe587392a890f59.jpg https://te.legra.ph/file/742e8351b9e1ffadec279.jpg https://te.legra.ph/file/09981361e5328a134f301.jpg https://te.legra.ph/file/cb16119ce03ee176f61aa.jpg https://te.legra.ph/file/22286db8625b388dc4b58.jpg https://te.legra.ph/file/428870361d507e412da8b.jpg https://te.legra.ph/file/680969e7aca6db904b8c1.jpg https://te.legra.ph/file/da065673967fb9151cee4.jpg https://te.legra.ph/file/13f51fe36db5ed64314b3.jpg https://te.legra.ph/file/267c261e642dde958a84a.jpg https://te.legra.ph/file/8628073743709c28f2087.jpg https://te.legra.ph/file/9678450125c36aff75692.jpg https://te.legra.ph/file/b96b23baf213570c791fe.jpg https://te.legra.ph/file/77144c064fc42cf4bf9b2.jpg https://te.legra.ph/file/dfe5abbb9fb84788697f6.jpg https://te.legra.ph/file/fde9da910d522a588eaf0.jpg https://te.legra.ph/file/35553f9cb429c42822aec.jpg https://te.legra.ph/file/75b73252882b3ce94218b.jpg https://te.legra.ph/file/b05444f73cc201656e17e.jpg https://te.legra.ph/file/10112037fb2635476a52b.jpg https://te.legra.ph/file/af822163a6cb7b7d48e31.jpg https://te.legra.ph/file/666e7a152d921a871f6f4.jpg https://te.legra.ph/file/4b19f80d954ae9e1a2605.jpg https://te.legra.ph/file/e0b072cd3d831019f78fe.jpg https://te.legra.ph/file/e86c93e56491f7010a29e.jpg https://te.legra.ph/file/71f813dd8cef6bdea3722.jpg https://te.legra.ph/file/8a917dd04677d4c88ea11.jpg https://te.legra.ph/file/25810e85b7385d29d4e3b.jpg https://te.legra.ph/file/29cf5e14d24caa40253df.jpg https://te.legra.ph/file/27bd43b076d58b12879dd.jpg https://te.legra.ph/file/f7db5cdb1ae1c19d67ef8.jpg https://te.legra.ph/file/f2cf3198a8908aff9e7de.jpg https://te.legra.ph/file/66adc90dc15827f2e23fa.jpg https://te.legra.ph/file/f5b26c70b38aa638d341f.jpg https://te.legra.ph/file/ee298bfba17d868eba348.jpg https://te.legra.ph/file/64694e942ed3c0988faa7.jpg https://te.legra.ph/file/5d773d2469b5677ad5a19.jpg https://te.legra.ph/file/7e9473f243f1c69b2df21.jpg https://te.legra.ph/file/4732cbc9ffa1cebbf5cd3.jpg https://te.legra.ph/file/424e027f57107a1e56364.jpg https://te.legra.ph/file/916dfdcddebc9aad89c7d.jpg https://te.legra.ph/file/162fbe5b38f79fdc91927.jpg https://te.legra.ph/file/5912d3a0225c08f5d24ae.jpg https://te.legra.ph/file/cd724de22aa94d9a668b6.jpg https://te.legra.ph/file/651beeeca9562b923d10f.jpg https://te.legra.ph/file/0233b42832da20411d6d3.jpg https://te.legra.ph/file/9b959943b88daf6dc8a46.jpg https://te.legra.ph/file/914c9e8cb2517e33a95c8.jpg https://te.legra.ph/file/ed5f1b9400e860ea6cfc6.jpg https://te.legra.ph/file/f9e4e5ab1cc53fc5bccce.jpg https://te.legra.ph/file/28dd1eb99198b04389a18.jpg https://te.legra.ph/file/e942f253189de32940612.jpg https://te.legra.ph/file/b4d5af8eff28702d9d54f.jpg https://te.legra.ph/file/fcd13f2b46d2bc45e2cf9.jpg https://te.legra.ph/file/b54b13bf6652b20601291.jpg https://te.legra.ph/file/39d558cf708da6d2f89fc.jpg https://te.legra.ph/file/97746b9242d90cf5486d7.jpg https://te.legra.ph/file/be450c9bcaeb26e63d36f.jpg https://te.legra.ph/file/c703ebe1f6b7f789756f2.jpg https://te.legra.ph/file/60619b9333ca127c46a27.jpg https://te.legra.ph/file/90cd4b496dc592336881d.jpg https://te.legra.ph/file/46b8b039bb3b002cd77e1.jpg https://te.legra.ph/file/fbf72a1216fe010ab8b2a.jpg https://te.legra.ph/file/9beca398de8e5d56e9a99.jpg https://te.legra.ph/file/085716fcbbde125c16a25.jpg https://te.legra.ph/file/3163bc3a08c18d005cced.jpg https://te.legra.ph/file/0a8d4c0a60ea7f32e185c.jpg https://te.legra.ph/file/70f7a05ba7bec6e20c99a.jpg https://te.legra.ph/file/4efe44c8ed8d2cae9d54c.jpg https://te.legra.ph/file/020b7facb4d767a946fc8.jpg https://te.legra.ph/file/9a9b5124caf080e88fb24.jpg https://te.legra.ph/file/474da91997373d43ed227.jpg https://te.legra.ph/file/1a8ae262e7671a4d56558.jpg https://te.legra.ph/file/4b2ea4a43cb04c368359c.jpg https://te.legra.ph/file/2759e8e4441ec8f6b0ef6.jpg https://te.legra.ph/file/cd2d1cd1ee2a90c0af858.jpg https://te.legra.ph/file/f27b5ac52ac95c2178abb.jpg https://te.legra.ph/file/0af7b2e4d360d75631e6a.jpg https://te.legra.ph/file/e817c6d5c39db7c75363b.jpg https://te.legra.ph/file/e50f9f8e697dfb4c13c9d.jpg https://te.legra.ph/file/e6435b6077acac93b8df0.jpg https://te.legra.ph/file/52c066f6a8960ba1234bf.jpg https://te.legra.ph/file/62c551b40de54a4950820.jpg https://te.legra.ph/file/e2dea679ae8f72a29106c.jpg https://te.legra.ph/file/4d1137283b786482a2f9c.jpg https://te.legra.ph/file/77244a1099982cb30d2b0.jpg https://te.legra.ph/file/5c6d3433a5ab06aaaf77e.jpg https://te.legra.ph/file/c9fc617d667b85ed4236f.jpg https://te.legra.ph/file/6ad5cded87e7b0cb6e224.jpg https://te.legra.ph/file/b5bccbbc8f0b8af7ea961.jpg https://te.legra.ph/file/6829ccfa46a1e52d5cc5a.jpg https://te.legra.ph/file/2d2d544f42d6416fb8e10.jpg https://te.legra.ph/file/9ae614be537eaac5b7b7d.jpg https://te.legra.ph/file/3191364559f1890791a04.jpg https://te.legra.ph/file/3ba56c1e24f329d5d714d.jpg https://te.legra.ph/file/94b649975668a93584cfb.jpg https://te.legra.ph/file/b7b86d0707bed40ae1aa1.jpg https://te.legra.ph/file/d51922d49a5e830b926cb.jpg https://te.legra.ph/file/e7059f6facb4528659775.jpg https://te.legra.ph/file/0e950d790043cf464f6bf.jpg https://te.legra.ph/file/49c2cae70066a3562a962.jpg https://te.legra.ph/file/d30d128ff9fd6c7e56995.jpg https://te.legra.ph/file/052bc49a6505a435f8732.jpg https://te.legra.ph/file/390d154932375e6223eac.jpg https://te.legra.ph/file/726184132d1351505c24a.jpg https://te.legra.ph/file/cd1283c66d292305d93ac.jpg https://te.legra.ph/file/46f4d6e7e512ee58fbf5b.jpg https://te.legra.ph/file/ecdfaab8a87fa83020eb9.jpg https://te.legra.ph/file/7ad528f3acea1426fc06e.jpg https://te.legra.ph/file/2ac591892210c11812f50.jpg https://te.legra.ph/file/dc3d54705cfec7feda3ce.jpg https://te.legra.ph/file/8e361f6365a958095f8a0.jpg https://te.legra.ph/file/e5ebcc836fa3b7dbb32ea.jpg https://te.legra.ph/file/216642cba9b042fdee685.jpg https://te.legra.ph/file/9d3a54bd2083aa65559a9.jpg https://te.legra.ph/file/519893c2c569009d7b1b1.jpg https://te.legra.ph/file/06a236ec80bd5d2bba415.jpg https://te.legra.ph/file/fc7cfdfe2724f39ff98fb.jpg https://te.legra.ph/file/e3736a1bca7c030d7cf4d.jpg https://te.legra.ph/file/bea85dc473eb7af053d27.jpg https://te.legra.ph/file/a0c0785e3c23715ba8eee.jpg https://te.legra.ph/file/c1f1c14f3eea27aa2ad26.jpg https://te.legra.ph/file/b854296a1c0e87df3f506.jpg https://te.legra.ph/file/1f3452336a5352f9e550a.jpg https://te.legra.ph/file/0ea5a00e36d1954b00407.jpg https://te.legra.ph/file/c8b9e09b3aa1354dd0c91.jpg https://te.legra.ph/file/5e48406eb9a4b5c5920cd.jpg https://te.legra.ph/file/80a366b4b044346105c32.jpg https://te.legra.ph/file/664953f075a7cf3311629.jpg https://te.legra.ph/file/b474f316e03a83bf1c30a.jpg https://te.legra.ph/file/b5cb3e132dcb01dbd03ba.jpg https://te.legra.ph/file/183d3f03f0eeced43bd1a.jpg https://te.legra.ph/file/5b844aee29ae548552e3a.jpg https://te.legra.ph/file/14d5ff33beb99eab2ace9.jpg https://te.legra.ph/file/11ba2014a58822bce4473.jpg https://te.legra.ph/file/d21b5e10591e08474edf8.jpg https://te.legra.ph/file/6f0f6a135c3908cd27f1e.jpg https://te.legra.ph/file/4a6d705d6fc15dc94b35f.jpg https://te.legra.ph/file/646903a9304a388c2eb13.jpg https://te.legra.ph/file/1e780d0f4342fbd68b730.jpg https://te.legra.ph/file/04efee61029d035174ba3.jpg https://te.legra.ph/file/3a3102cd6b7b7f9d594d5.jpg https://te.legra.ph/file/feb2240b3058ca3da9a8f.jpg https://te.legra.ph/file/c6e7d2490bbae4af352b6.jpg https://te.legra.ph/file/37b7af12f3aaab2373f5d.jpg https://te.legra.ph/file/3a9907c4d3a3bbe6292c4.jpg https://te.legra.ph/file/2c53170a276d9157744cc.jpg https://te.legra.ph/file/7d3ae66ff3a8adc4e17e6.jpg https://te.legra.ph/file/26f341f2abebdadd1dda5.jpg https://te.legra.ph/file/08e3cac96d1eb32718d42.jpg https://te.legra.ph/file/76a1dbaaf4499eeed4e50.jpg https://te.legra.ph/file/5ba6afc121034031df3ac.jpg https://te.legra.ph/file/2d40e7ba1d05ed45d069d.jpg https://te.legra.ph/file/ecd991e1d3945684c94a1.jpg https://te.legra.ph/file/26ed18b969d13982e71af.jpg https://te.legra.ph/file/d0c84ac37987aab950c7f.jpg https://te.legra.ph/file/0abfa9393fb55beb9289a.jpg https://te.legra.ph/file/c695a98e09a4cf10eb927.jpg https://te.legra.ph/file/8610711ac8846c10eb62f.jpg https://te.legra.ph/file/5bfabcfc65a26fa11caa3.jpg https://te.legra.ph/file/11fe1b968001fd77d6d8e.jpg https://te.legra.ph/file/26386f860b6c8131a59ba.jpg https://te.legra.ph/file/3743405e153287b59cf3d.jpg https://te.legra.ph/file/9b39f409788bdcf9eac91.jpg https://te.legra.ph/file/39cbe09eef7c918a4391b.jpg https://te.legra.ph/file/1cf8745322ffd8639dfda.jpg https://te.legra.ph/file/1bf3115ae7f5cd88986f5.jpg https://te.legra.ph/file/e1ec54d2f56f0d5101f28.jpg https://te.legra.ph/file/0e2092e1589446781bf70.jpg https://te.legra.ph/file/6cbf6975eb3c3ffc7f27f.jpg https://te.legra.ph/file/8a7e046c9ede68c26c3aa.jpg https://te.legra.ph/file/cd6b3719e17249861937c.jpg https://te.legra.ph/file/3d07a8b94806963518def.jpg https://te.legra.ph/file/d19c396991d5966485592.jpg https://te.legra.ph/file/9f99358c11f2077f25a3d.jpg https://te.legra.ph/file/01c72a3a1ca1a5bb7c38a.jpg https://te.legra.ph/file/75e966647295039773b65.jpg https://te.legra.ph/file/3cbca61260fdbc272d87a.jpg https://te.legra.ph/file/18bb28838c4c0fa11a1f6.jpg https://te.legra.ph/file/572db97509a9abd76b6a2.jpg https://te.legra.ph/file/36ac1ebf5671a54065a7a.jpg https://te.legra.ph/file/be01be61bd5c74db54c93.jpg https://te.legra.ph/file/0ced2c5d77340d88a82a0.jpg https://te.legra.ph/file/1074468ba57037b52dce2.jpg https://te.legra.ph/file/0793caa8710ceb3c10ac4.jpg https://te.legra.ph/file/c1fcc6c355655b9792de2.jpg https://te.legra.ph/file/02da428523c78fef22c7d.jpg https://te.legra.ph/file/f065b0f45e97b117fb1b2.jpg https://te.legra.ph/file/620d404c2e9bb51447638.jpg https://te.legra.ph/file/c724a419888966108ab46.jpg https://te.legra.ph/file/4af7e5fc54ff6585e440b.jpg https://te.legra.ph/file/202deb55d3ed6594abde7.jpg https://te.legra.ph/file/48e1a9652be39af246202.jpg https://te.legra.ph/file/1b4b09f0f87f38705f12a.jpg https://te.legra.ph/file/5b42579bc9f93712bfc6b.jpg https://te.legra.ph/file/0e3483cc45ca89914c7de.jpg https://te.legra.ph/file/78392ac491a0839c9e3de.jpg https://te.legra.ph/file/54c9c5ab48725ce648913.jpg https://te.legra.ph/file/24d3a33e5456d94f7eb56.jpg https://te.legra.ph/file/3bed5e5eb39df7004d94c.jpg https://te.legra.ph/file/b5d730c349712d63051ac.jpg https://te.legra.ph/file/df612ecf4e650994e6b93.jpg https://te.legra.ph/file/657e26d0beaa752189e77.jpg https://te.legra.ph/file/7c06dc99dc430e8ad5f77.jpg https://te.legra.ph/file/ae945b098ea6d428b51e1.jpg https://te.legra.ph/file/bb38746471340fb80327b.jpg https://te.legra.ph/file/329ccec4ccbcb27ef9a0d.jpg https://te.legra.ph/file/db2e71e45b0bf562e4500.jpg https://te.legra.ph/file/ff6aa7da670a683d1efbf.jpg https://te.legra.ph/file/3e352b209ba8dfe84a0db.jpg https://te.legra.ph/file/5237384baecb9237e81f7.jpg https://te.legra.ph/file/cc5bf57c806d7a0fe477a.jpg https://te.legra.ph/file/de5bd735a1f0e4853072d.jpg https://te.legra.ph/file/6939a65e435c4c3abcf60.jpg https://te.legra.ph/file/f3529fefe1c6ebaf98324.jpg https://te.legra.ph/file/588714b4fce5bfa825517.jpg https://te.legra.ph/file/6a8682f096eaddb82010e.jpg https://te.legra.ph/file/c7a843a69f1df810aa9a3.jpg https://te.legra.ph/file/a5b4f5163974d74be6719.jpg https://te.legra.ph/file/aa59932d9952d41f86a5e.jpg https://te.legra.ph/file/e291304f49fc45f60294f.jpg https://te.legra.ph/file/315c5956e3ffcd5a03a78.jpg https://te.legra.ph/file/6d9561796d91b6aab4b69.jpg https://te.legra.ph/file/da89a2bd2fc5593633376.jpg https://te.legra.ph/file/929e10f0060b9b3412636.jpg https://te.legra.ph/file/9c322e27bee59353ab2a4.jpg https://te.legra.ph/file/e0a43bd433226d083c198.jpg https://te.legra.ph/file/44e279de429dc009ea285.jpg https://te.legra.ph/file/e07610210dc13fb4430f6.jpg https://te.legra.ph/file/18ebac2a15d490c27f6f9.jpg https://te.legra.ph/file/4d2b89d4791f252c8e568.jpg https://te.legra.ph/file/95e99e39e0580e2df5759.jpg https://te.legra.ph/file/2f2eca72f0bcc47bee74b.jpg https://te.legra.ph/file/633ae6ea1de4d6bf4529f.jpg https://te.legra.ph/file/afd32d3d32d0b303eff0a.jpg https://te.legra.ph/file/cb15cf8bf6140ec67b43c.jpg https://te.legra.ph/file/61b1c28c6092f9fc42e18.jpg https://te.legra.ph/file/c00b08b2ed449f33eaac4.jpg https://te.legra.ph/file/e63b4eabb313eef478b41.jpg https://te.legra.ph/file/64d79a3b63aa5be8e0b55.jpg https://te.legra.ph/file/38c50b1e5f1eed8e90d89.jpg https://te.legra.ph/file/d0679d605156366707759.jpg https://te.legra.ph/file/5a96e07c78ece1153ba87.jpg https://te.legra.ph/file/b479f8c1a8a98a50e9cfb.jpg https://te.legra.ph/file/946958e8a248edf5a8aef.jpg https://te.legra.ph/file/df9676bda8c7468d2c3a7.jpg https://te.legra.ph/file/9a8870929aa504bd3e6a9.jpg https://te.legra.ph/file/7388b1994b9058bd0ae18.jpg https://te.legra.ph/file/8e63de58dc4ae7d937567.jpg https://te.legra.ph/file/e13b7b139630ae0a7f51b.jpg https://te.legra.ph/file/0c0afa92850b077f2c5c3.jpg https://te.legra.ph/file/92bf8f243bb9b77dbdd8c.jpg https://te.legra.ph/file/2cbb3a01012539bd70355.jpg https://te.legra.ph/file/8043665bc213f09a620e5.jpg https://te.legra.ph/file/52cec5b74c8aad413980f.jpg https://te.legra.ph/file/b371263652f2c4f3d543b.jpg https://te.legra.ph/file/d0554a8de0e88629f121e.jpg https://te.legra.ph/file/15f64185824bfff88f34e.jpg https://te.legra.ph/file/dc09386532a55678fc1dd.jpg https://te.legra.ph/file/45e96735c28126b001e9b.jpg https://te.legra.ph/file/6d9e280c157778335026e.jpg https://te.legra.ph/file/ed316c3db531071df8b1d.jpg https://te.legra.ph/file/46b9039e3a7291a4003dd.jpg https://te.legra.ph/file/51e109de258db3796b27c.jpg https://te.legra.ph/file/7025a28a57170f9e6b6f8.jpg https://te.legra.ph/file/e72755b692d06e14a0b04.jpg https://te.legra.ph/file/7be673411b2fb1003d393.jpg https://te.legra.ph/file/3d2e94cb99612ccd4b258.jpg https://te.legra.ph/file/822b28e17c766a8befbc0.jpg https://te.legra.ph/file/8c76e299bcf1d80120a81.jpg https://te.legra.ph/file/b3f9d9ada445c44e13d30.jpg https://te.legra.ph/file/369958493bda772321af5.jpg https://te.legra.ph/file/2c8ebd7aa2c58fefd7eba.jpg https://te.legra.ph/file/83c234dd08c03844217cf.jpg https://te.legra.ph/file/91935d88270e250258d35.jpg https://te.legra.ph/file/e6c23d6a37493c271cbf5.jpg https://te.legra.ph/file/4281594d89ca784ef9cfe.jpg https://te.legra.ph/file/3ffcc823eceb4ba34ef20.jpg https://te.legra.ph/file/2bef8bb57246285f7129d.jpg https://te.legra.ph/file/0228ae704ecaab7a04726.jpg https://te.legra.ph/file/15ce009d76b8ac111d033.jpg https://te.legra.ph/file/2d168e9b865030b58289f.jpg https://te.legra.ph/file/88fad9b8033340b1fcf6d.jpg https://te.legra.ph/file/fc4163c9e4ec9c343d5d1.jpg https://te.legra.ph/file/cc18de3d2e6388d505ad3.jpg https://te.legra.ph/file/b0f2305f8d636fab396f3.jpg https://te.legra.ph/file/2e09960a7f11422a951cf.jpg https://te.legra.ph/file/61ca192d95e81b1873049.jpg https://te.legra.ph/file/ceea29fd7fad621f8c857.jpg https://te.legra.ph/file/2b4e2e793d2bedb664468.jpg https://te.legra.ph/file/a898bd43e8e65de5b89bc.jpg https://te.legra.ph/file/b13fa07396e6b79c3da41.jpg https://te.legra.ph/file/9213eca38cb11c2e4c399.jpg https://te.legra.ph/file/6f5554506900020e54296.jpg https://te.legra.ph/file/313c2958aebb26ae5d89f.jpg https://te.legra.ph/file/732e7955fae7f528d9889.jpg https://te.legra.ph/file/572d5d929f684d9f02ff5.jpg https://te.legra.ph/file/fc0d5c3ac7d1a9de41ddf.jpg https://te.legra.ph/file/bc0322bf7acb66ebe019a.jpg https://te.legra.ph/file/7263d2049c66545650d6b.jpg https://te.legra.ph/file/986cb88323920748871d0.jpg https://te.legra.ph/file/7125493fdf14cbec5b364.jpg https://te.legra.ph/file/c4be3c089f23f0a082701.jpg https://te.legra.ph/file/9d4d0a55a9253fc7657b3.jpg https://te.legra.ph/file/b499b0ede4094d40b7bf7.jpg https://te.legra.ph/file/3286595263ecaecb3d9fd.jpg https://te.legra.ph/file/8ee4077c566dd547b1531.jpg https://te.legra.ph/file/f109402d4e796e0069067.jpg https://te.legra.ph/file/1649b7a8a5c510bc70a6e.jpg https://te.legra.ph/file/3fa7f527818fbbc886aef.jpg https://te.legra.ph/file/95082a0307471f4cbf1e8.jpg https://te.legra.ph/file/f016ec4c55afe112a18c6.jpg https://te.legra.ph/file/ad4061212b7c1dd519f8f.jpg https://te.legra.ph/file/83c20699eeb9e43bb1505.jpg https://te.legra.ph/file/5f7596b389f47f7385222.jpg https://te.legra.ph/file/04c404621e2f905120e8b.jpg https://te.legra.ph/file/773fb29c596d3d394f97f.jpg https://te.legra.ph/file/129873619211f3bad5e7f.jpg https://te.legra.ph/file/2c90a1385e971fe214580.jpg https://te.legra.ph/file/6d6e099d17f588d0fcb60.jpg https://te.legra.ph/file/ffcf3f19dd4e49d3599c0.jpg https://te.legra.ph/file/3acf2921449bf2bebedf5.jpg https://te.legra.ph/file/ba54f7c86bc1df59cfcd2.jpg https://te.legra.ph/file/b15c1b75c055e31357305.jpg https://te.legra.ph/file/780e4d93f318e7c3cf8b6.jpg https://te.legra.ph/file/4ba4f7f40f2615a365683.jpg https://te.legra.ph/file/acdda767a13c894868e5c.jpg https://te.legra.ph/file/d452fe915e5dc3261acdf.jpg https://te.legra.ph/file/60a0c35b1d7ac47a9bdab.jpg https://te.legra.ph/file/b355494671a5b7b9d83ad.jpg https://te.legra.ph/file/f43c6c82f665d63839f10.jpg https://te.legra.ph/file/1d673522f6430570e3447.jpg https://te.legra.ph/file/dfea08b0a8712e5bf06ab.jpg https://te.legra.ph/file/5db8360245379a2c5d8a9.jpg https://te.legra.ph/file/9b0fe886c0e623a580817.jpg https://te.legra.ph/file/3e7ae8b84e2fff6e03b09.jpg https://te.legra.ph/file/3111ab9289851c1f53555.jpg https://te.legra.ph/file/a322e331a4bffb9efcbab.jpg https://te.legra.ph/file/63c44b3c6e79b9059997b.jpg https://te.legra.ph/file/701b9f6a8ecce04a46ca8.jpg https://te.legra.ph/file/98747160d7cbf0ddcd895.jpg https://te.legra.ph/file/44d45ae7ed55d08e2f5d2.jpg https://te.legra.ph/file/5195f2013f2f5a38e8a02.jpg https://te.legra.ph/file/ed002df5186e378b7954d.jpg https://te.legra.ph/file/6b438191973b1d7cb0c38.jpg https://te.legra.ph/file/4d2e0425d66e97be1e211.jpg https://te.legra.ph/file/beb182820b836de1274a0.jpg https://te.legra.ph/file/8bfd9708015478544bc5c.jpg https://te.legra.ph/file/eb29ae656e77c2a91ccb4.jpg https://te.legra.ph/file/c3bf7ea52c82901cb9bc6.jpg https://te.legra.ph/file/570beacafba0b5bbc0a71.jpg https://te.legra.ph/file/e40225f4590caff86fb32.jpg https://te.legra.ph/file/8a63b591119aaf2204d49.jpg https://te.legra.ph/file/3e2c43092f25598203dec.jpg https://te.legra.ph/file/f1801786bdbec5b13efce.jpg https://te.legra.ph/file/ffc8463149c2f20c72e20.jpg https://te.legra.ph/file/14ea6643bb997c253d81a.jpg https://te.legra.ph/file/5d652031a5f47bd71676d.jpg https://te.legra.ph/file/55de6bf6aa94cf6ddfba2.jpg https://te.legra.ph/file/e851e2bbf94b007048594.jpg https://te.legra.ph/file/eb4a66b11a1727cce9c5e.jpg https://te.legra.ph/file/9d1e1ff892dd6e0b1d447.jpg https://te.legra.ph/file/b79e3de6b61eb7db792d4.jpg https://te.legra.ph/file/06e91c093b567d9ea3f92.jpg https://te.legra.ph/file/00e67cc98f8b46f5ee56e.jpg https://te.legra.ph/file/ca10eea5d892bcf4c7b61.jpg https://te.legra.ph/file/953e9c9e6659d16ac28cc.jpg https://te.legra.ph/file/eb8f25d201238f3527470.jpg https://te.legra.ph/file/348f39345d828bc4875d0.jpg https://te.legra.ph/file/4c8265563f9865e6098e7.jpg https://te.legra.ph/file/a3662667eb4a421411133.jpg https://te.legra.ph/file/a1b11e7dcadb5f4df520c.jpg https://te.legra.ph/file/2d19499b4b9c8b4159d99.jpg https://te.legra.ph/file/cf3ad50022a99683a3890.jpg https://te.legra.ph/file/c412d54b0a84c58db0eb2.jpg https://te.legra.ph/file/0b61d40c18b8dfac55fbb.jpg https://te.legra.ph/file/737251f750c9ec43c56a0.jpg https://te.legra.ph/file/33ff8d8f2f7f3341e974d.jpg https://te.legra.ph/file/b41451e507b8c67fc54d3.jpg https://te.legra.ph/file/aa751a6ab60df241fe903.jpg https://te.legra.ph/file/09a7c7a8ffb940cac7713.jpg https://te.legra.ph/file/ee93f92c3626c42d0773a.jpg https://te.legra.ph/file/b2561921e72a783498edf.jpg https://te.legra.ph/file/9b3a2aa3ea779d6b93a46.jpg https://te.legra.ph/file/aef6635f8e7c62393ec41.jpg https://te.legra.ph/file/a08dbb72878ffdfe511d0.jpg https://te.legra.ph/file/b884ff0cfc9eb30c9ae13.jpg https://te.legra.ph/file/19502fb05e7ae1b2ea73e.jpg https://te.legra.ph/file/ea13e61c5b7ff79754d03.jpg https://te.legra.ph/file/bec924af1c9a1e3cbcc21.jpg https://te.legra.ph/file/0c01bd62b50dee1700e03.jpg https://te.legra.ph/file/73fe3d4ec4e3fed8f0210.jpg https://te.legra.ph/file/bd9dc917a0e25415777d7.jpg https://te.legra.ph/file/8e1e116972a253e677c81.jpg https://te.legra.ph/file/3f9567b723e9e1ea54f0a.jpg https://te.legra.ph/file/e164128afc7eb3eb44996.jpg https://te.legra.ph/file/3f097c3766678ea6ec57e.jpg https://te.legra.ph/file/ac182e1bf67db2a002872.jpg https://te.legra.ph/file/461a0ca48690b53126fa4.jpg https://te.legra.ph/file/a47eedafd9066f9a0e25c.jpg https://te.legra.ph/file/193b5eef49d93e0eb4cc8.jpg https://te.legra.ph/file/e6966480d95ba71ac4bc9.jpg https://te.legra.ph/file/327a3bf7928cd34c70143.jpg https://te.legra.ph/file/fd9d776f6ad8995e48329.jpg https://te.legra.ph/file/1531b67dc5febeacac83b.jpg https://te.legra.ph/file/3918f2b8cb52e91189045.jpg https://te.legra.ph/file/68e597ac5b700bbdf1ebd.jpg https://te.legra.ph/file/ca7c2b4f58d40f19a3418.jpg https://te.legra.ph/file/06ab8aec03451b78ff9af.jpg https://te.legra.ph/file/37caa6bd70a67c6155f57.jpg https://te.legra.ph/file/902572833cb5c8a4a2de4.jpg https://te.legra.ph/file/76825932ca7576ae07bae.jpg https://te.legra.ph/file/0c691218ee4708b0bed36.jpg https://te.legra.ph/file/e52795261cf23b5164df1.jpg https://te.legra.ph/file/1419dbb94daa103c226b0.jpg https://te.legra.ph/file/ad41771660885873c9f97.jpg https://te.legra.ph/file/2be2397cdcb663f4309a4.jpg https://te.legra.ph/file/82fd5efa724f6b1c4badf.jpg https://te.legra.ph/file/b10fd032fc3bdb27619ae.jpg https://te.legra.ph/file/3e45e1a8a16000f797947.jpg https://te.legra.ph/file/797a7fe3660fc3e27dc39.jpg https://te.legra.ph/file/6e2108adb8dea1676cae5.jpg https://te.legra.ph/file/ec7bd13911b0d12f52abc.jpg https://te.legra.ph/file/28172acba18af9a84a229.jpg https://te.legra.ph/file/72435e520010da381db0c.jpg https://te.legra.ph/file/dfab635161078e3c45e77.jpg https://te.legra.ph/file/211d1f2fe97374d66e645.jpg https://te.legra.ph/file/49ea535ccdb5d2c998b7f.jpg https://te.legra.ph/file/569bb865604f6223b7885.jpg https://te.legra.ph/file/d1e4de9eff5842e23d9e7.jpg https://te.legra.ph/file/088c38e642cf121134984.jpg https://te.legra.ph/file/0fbde45ef12945efd8bc6.jpg https://te.legra.ph/file/f08fc2c15c9255ae71a53.jpg https://te.legra.ph/file/383b538bddc5f83289e77.jpg https://te.legra.ph/file/1f01d9c90ffd4b0f41830.jpg https://te.legra.ph/file/cfa0a092b13f10293a7d7.jpg https://te.legra.ph/file/513ea2d7ceb3ff67e68de.jpg https://te.legra.ph/file/9fe3b6c1eae27228d8a56.jpg https://te.legra.ph/file/8384339fba12775273c85.jpg https://te.legra.ph/file/6b06cf83a232dcb4a6481.jpg https://te.legra.ph/file/dbb4f51ad81d96793fa4a.jpg https://te.legra.ph/file/8e1a53fcb3fa413178acd.jpg https://te.legra.ph/file/20743a706a679ea1a21af.jpg https://te.legra.ph/file/7f4343f33fe24056065f9.jpg https://te.legra.ph/file/f83dd607934b2f1a3d0dd.jpg https://te.legra.ph/file/5a8868c1b76cc8ed5ef67.jpg https://te.legra.ph/file/3e4b4ea6610276feb7123.jpg https://te.legra.ph/file/19b9697fd0f0f0bd00356.jpg https://te.legra.ph/file/44b72a9a2eae171a19f70.jpg https://te.legra.ph/file/ecfabeb15dd989108f4b9.jpg https://te.legra.ph/file/1c3ea8088573e3ba5f70f.jpg https://te.legra.ph/file/c7a80eb9960b7ff19112b.jpg https://te.legra.ph/file/21ad900715e9124920753.jpg https://te.legra.ph/file/fe97b8685cff19cf674c5.jpg https://te.legra.ph/file/f12a0f4c52a5ae29cfe0e.jpg https://te.legra.ph/file/11f9690f987ee92cbec95.jpg https://te.legra.ph/file/d2be4007b9f5534d77471.jpg https://te.legra.ph/file/ffcfa2d8e7584de87897f.jpg https://te.legra.ph/file/bee7a474601d38d20d170.jpg https://te.legra.ph/file/b68b2ea97aeb0aaa83218.jpg https://te.legra.ph/file/f76149d0306174c8afb80.jpg https://te.legra.ph/file/e2152fede1899ab42b6ba.jpg https://te.legra.ph/file/e085a2373a16c75aef8a2.jpg https://te.legra.ph/file/f3ddf70e4372b98e89684.jpg https://te.legra.ph/file/7482266a3cf8bafde739e.jpg https://te.legra.ph/file/f5066d703aa2bd0f35a61.jpg https://te.legra.ph/file/0922acff3e0127a7f915e.jpg https://te.legra.ph/file/eb011067c74c05507a1ec.jpg https://te.legra.ph/file/76601e3480560796c4861.jpg https://te.legra.ph/file/1052fb5f40c96f96c8212.jpg https://te.legra.ph/file/12a6492774513a162fed0.jpg https://te.legra.ph/file/4d8a5026475b35771ff80.jpg https://te.legra.ph/file/2c6c5434e07e8b18bd77c.jpg https://te.legra.ph/file/51d852ff4fc0d43633cc9.jpg https://te.legra.ph/file/f90bd68e1aa9bef257b76.jpg https://te.legra.ph/file/5a9b74854586d130b1627.jpg https://te.legra.ph/file/dfbfd6b34d7786b8a0e08.jpg https://te.legra.ph/file/ff1a6f82a68d43805d32e.jpg https://te.legra.ph/file/c5157aab675946f9242e1.jpg https://te.legra.ph/file/1f345568a573fdd580fc9.jpg https://te.legra.ph/file/b1c42adb748ee505a7783.jpg https://te.legra.ph/file/d4da1582ea220056cf82a.jpg https://te.legra.ph/file/1ed5b67b9163b2d47c400.jpg https://te.legra.ph/file/bcbbf6ae7bc3c3f4c4db6.jpg https://te.legra.ph/file/65624a7dbf3d0dabcbb3c.jpg https://te.legra.ph/file/91122ff710ff55c7daee9.jpg https://te.legra.ph/file/661dc512fa62c9e2f702e.jpg https://te.legra.ph/file/0a7f266d63eb61899881c.jpg https://te.legra.ph/file/49d7c3972483840e5807f.jpg https://te.legra.ph/file/34e4a035f75dfb79762d1.jpg https://te.legra.ph/file/5bd7f0d9fb244c4e219e6.jpg https://te.legra.ph/file/76082048ff066e3ef94bb.jpg https://te.legra.ph/file/fb95d08af43d1dbbc9770.jpg https://te.legra.ph/file/ce9848ec360dd1e440af4.jpg https://te.legra.ph/file/bd50c0f975c816a4cf14a.jpg https://te.legra.ph/file/4dff510a256440e36be4a.jpg https://te.legra.ph/file/5363ada3e021460b0aad1.jpg https://te.legra.ph/file/3908f17f8fd58fb6b9c2c.jpg https://te.legra.ph/file/a745c172ccc8a70154fa5.jpg https://te.legra.ph/file/1d9d90c7aa71e1069b425.jpg https://te.legra.ph/file/ce15ebf1e433b107a4893.jpg https://te.legra.ph/file/9a72a92cd27d04f47b3dd.jpg https://te.legra.ph/file/4fae941526e6b862d6767.jpg https://te.legra.ph/file/077b7db56f2e93fbf789c.jpg https://te.legra.ph/file/0b27c0dafeb731e5bfcc6.jpg https://te.legra.ph/file/ee335b5f195c761b2b779.jpg https://te.legra.ph/file/24eb6fd9e5fe74a421056.jpg https://te.legra.ph/file/df37a2a92c7255109d729.jpg https://te.legra.ph/file/1a0c684aeb9909736ddd8.jpg https://te.legra.ph/file/742b9377b2eb5efaff810.jpg https://te.legra.ph/file/48a73939b17388292a7ea.jpg https://te.legra.ph/file/c53e8b01e4cdf9486e385.jpg https://te.legra.ph/file/4fb962b56cc886e000498.jpg https://te.legra.ph/file/13602d6f86103d5e5b1b5.jpg https://te.legra.ph/file/e700df235284adfe1b4ad.jpg https://te.legra.ph/file/4b6fb86adafa3ff0e770b.jpg https://te.legra.ph/file/b9de91e4b960597f87d5d.jpg https://te.legra.ph/file/5b656d4599b5a3aae3dde.jpg https://te.legra.ph/file/b09db55bca03f34355ce3.jpg https://te.legra.ph/file/bea7abf50e5d4316adb4a.jpg https://te.legra.ph/file/cec782c98a5394f0449e7.jpg https://te.legra.ph/file/a96afb99c8af512da3812.jpg https://te.legra.ph/file/c9aaf85a4c99a81be3587.jpg https://te.legra.ph/file/7614c4b9920715591f80f.jpg https://te.legra.ph/file/4992ec021438edbb9bace.jpg https://te.legra.ph/file/556ad83d26c2ef66d1a16.jpg https://te.legra.ph/file/f2007267a5746e9494820.jpg https://te.legra.ph/file/cc38d17278ffc2eeda419.jpg https://te.legra.ph/file/1bae952f053d54e6b368d.jpg https://te.legra.ph/file/6ae124db75f78e3d46e0e.jpg https://te.legra.ph/file/c96506445a40eb407cd3d.jpg https://te.legra.ph/file/1e394830b4c0ea6260982.jpg https://te.legra.ph/file/4f07759398cf5f1ff359b.jpg https://te.legra.ph/file/1bb3c733467ac329fe72e.jpg https://te.legra.ph/file/6c811e2d0621feaacd33b.jpg https://te.legra.ph/file/e429f6346da0b9c7bb67b.jpg https://te.legra.ph/file/c1c9154f4d9b86910f075.jpg https://te.legra.ph/file/6cce3a81a267e3202f354.jpg https://te.legra.ph/file/871702fb713c720b40292.jpg https://te.legra.ph/file/9c9a37637ca0427be4864.jpg https://te.legra.ph/file/f8ae78886633476616914.jpg https://te.legra.ph/file/dc7a07de5ee62c91eb1fc.jpg https://te.legra.ph/file/86ee9010063f8bbaf0ac5.jpg https://te.legra.ph/file/122c1f9df00b368283d86.jpg https://te.legra.ph/file/f209f0350553fadb595a9.jpg https://te.legra.ph/file/d218a8f1654819d21c4a4.jpg https://te.legra.ph/file/0d383f64930d9def6ba2a.jpg https://te.legra.ph/file/7186d057c1dabbf2b4caf.jpg https://te.legra.ph/file/8bde551af58fa8d84ec49.jpg https://te.legra.ph/file/cb8290518bb3f66a01965.jpg https://te.legra.ph/file/2869b095e83a801227f2f.jpg https://te.legra.ph/file/3619497128d84b4acb5f5.jpg https://te.legra.ph/file/1cbe85bbb21d318f6326f.jpg https://te.legra.ph/file/08649d240edd610595721.jpg https://te.legra.ph/file/9a2925ddc5ad087132236.jpg https://te.legra.ph/file/eab276d30df4e85ff4afd.jpg https://te.legra.ph/file/112cb0008176b459c68e3.jpg https://te.legra.ph/file/b125bf764780d8b595235.jpg https://te.legra.ph/file/65cb9b23ab61b56d9501e.jpg https://te.legra.ph/file/c8513bdbd428faacc98cf.jpg https://te.legra.ph/file/b6bf7ca717e58c4e04a36.jpg https://te.legra.ph/file/2d1bf927a9973e6be4d0f.jpg https://te.legra.ph/file/1e0c58ebe2dac21a1a497.jpg https://te.legra.ph/file/208637098ab205548b7c0.jpg https://te.legra.ph/file/cf1e72e4184dc27f8e589.jpg https://te.legra.ph/file/f2010dd6607a07fe47992.jpg https://te.legra.ph/file/a185e0daf4ba04553d3ea.jpg https://te.legra.ph/file/6b3656998e183b3696253.jpg https://te.legra.ph/file/2a85396043748c8fac4ed.jpg https://te.legra.ph/file/18acf9dc4facf27b897ba.jpg https://te.legra.ph/file/2ff3106e64bfeca158486.jpg https://te.legra.ph/file/14fbac7ddb2fee36268ad.jpg https://te.legra.ph/file/23909c1e12c17aca5cfe7.jpg https://te.legra.ph/file/bd36b87c3e195378986fe.jpg https://te.legra.ph/file/4e0934863525d406c730d.jpg https://te.legra.ph/file/9a83158ea3db6ea82bc1b.jpg https://te.legra.ph/file/979d2ad8165943c681b43.jpg https://te.legra.ph/file/d04f69d8070e60e7df829.jpg https://te.legra.ph/file/bb76ad524c3893ca163cd.jpg https://te.legra.ph/file/ccaf44902890e39f0187b.jpg https://te.legra.ph/file/4268d0494b0835b9d9aeb.jpg https://te.legra.ph/file/c1a019011a192b76de90a.jpg https://te.legra.ph/file/4d4c4bc83f209465afdd8.jpg https://te.legra.ph/file/8f2add5f57ea6798c935f.jpg https://te.legra.ph/file/0c56ed39406e424534a9d.jpg https://te.legra.ph/file/8128f1cbef4d62c28be85.jpg https://te.legra.ph/file/3c597902a61bfd397b714.jpg https://te.legra.ph/file/abd8a5213d5d746dc5374.jpg https://te.legra.ph/file/054796a19d040133cb496.jpg https://te.legra.ph/file/8e2ce303d7763cd90997e.jpg https://te.legra.ph/file/45af89ffe1aee2e66b546.jpg https://te.legra.ph/file/6c2369005b93fbc20441e.jpg https://te.legra.ph/file/b55e284952e982e5425f0.jpg https://te.legra.ph/file/ab4b7dfc725d408852404.jpg https://te.legra.ph/file/2a51311db14b503d5fcd7.jpg https://te.legra.ph/file/4c12ecd0c672d8ab0312c.jpg https://te.legra.ph/file/d79d8d28ed8cc263c6e9e.jpg https://te.legra.ph/file/eb199a5e77789a6127d06.jpg https://te.legra.ph/file/66e39bbd87eaa699d8c54.jpg https://te.legra.ph/file/865f9610f0b7fdaa3a3e4.jpg https://te.legra.ph/file/2dbe08a7815c49c584170.jpg https://te.legra.ph/file/67313bfbedf352a723b27.jpg https://te.legra.ph/file/37588d338f6598e943cb6.jpg https://te.legra.ph/file/f16bd8685d1064dd17969.jpg https://te.legra.ph/file/aa312bfa89dbd3ec74dea.jpg https://te.legra.ph/file/60c6b5b018e3db7a8e3a5.jpg https://te.legra.ph/file/985d0293f88e2f4b63556.jpg https://te.legra.ph/file/5fab96bf35b7e3e8b738d.jpg https://te.legra.ph/file/3e3be924ee18e639fb283.jpg https://te.legra.ph/file/7c5100dff3a6b42bd3c3a.jpg https://te.legra.ph/file/9ae8d33242302cd67035a.jpg https://te.legra.ph/file/a44c93da1b6cc887aa29d.jpg https://te.legra.ph/file/486aa97325db889c6b579.jpg https://te.legra.ph/file/68ba27aae9a295cec1000.jpg https://te.legra.ph/file/92ebaeeb1ab41ef07d82d.jpg https://te.legra.ph/file/cde408952f13bbd2c1ef3.jpg https://te.legra.ph/file/069212ad5dd24ae52864d.jpg https://te.legra.ph/file/74549ba9b6d550a483033.jpg https://te.legra.ph/file/4c5b1a7ff288f26ac7eb1.jpg https://te.legra.ph/file/d3fc91545e8670489a80e.jpg https://te.legra.ph/file/d51c1e7f4154a5f9850b0.jpg https://te.legra.ph/file/c47b6d3a5bd3f22824f42.jpg https://te.legra.ph/file/e44d2eadc2adca49c5abe.jpg https://te.legra.ph/file/603feeee7406fd24f1478.jpg https://te.legra.ph/file/0e9b213d69529094486b7.jpg https://te.legra.ph/file/bd0e3be43ada89b350d2a.jpg https://te.legra.ph/file/4645a42f66ca9bb226ab1.jpg https://te.legra.ph/file/56dcd2a1b63ed1d88ded2.jpg https://te.legra.ph/file/14d86e3d214b9977c5063.jpg https://te.legra.ph/file/021df38646a3242e95126.jpg https://te.legra.ph/file/48dd97d63656c68f25f58.jpg https://te.legra.ph/file/121125678360feaad7b4d.jpg https://te.legra.ph/file/a82d4b9c6c229894b0afe.jpg https://te.legra.ph/file/a8c57ed17e7e17f009026.jpg https://te.legra.ph/file/e063dcfe02715e4ee1f67.jpg https://te.legra.ph/file/14a91c4d5486c32896e80.jpg https://te.legra.ph/file/1bc650da77f39fed1d9a6.jpg https://te.legra.ph/file/b9be4f340b58d0a4f133e.jpg https://te.legra.ph/file/cda04df9a525a3ad6f4f6.jpg https://te.legra.ph/file/41bfe040eaed760fa4dfe.jpg https://te.legra.ph/file/946fc277cd8723d669623.jpg https://te.legra.ph/file/157cbdebfc3457db8aedf.jpg https://te.legra.ph/file/a08858c0c076753fedc28.jpg https://te.legra.ph/file/42e7c0b8f9b0a5f2c9fc3.jpg https://te.legra.ph/file/cf10400702265598ea696.jpg https://te.legra.ph/file/27dd53d90aef830d22d18.jpg https://te.legra.ph/file/d4352b7e3758128d831ae.jpg https://te.legra.ph/file/c074a97e65f0e60c07203.jpg https://te.legra.ph/file/db7fba7bd6b4f86c676bf.jpg https://te.legra.ph/file/a2042adbd5f8ffcbaae12.jpg https://te.legra.ph/file/03df0db77b4175df5407e.jpg https://te.legra.ph/file/e5743ec8908aa6cf848d8.jpg https://te.legra.ph/file/4deac12a958bd7dfd94f3.jpg https://te.legra.ph/file/1ed871327169a8e03bb0f.jpg https://te.legra.ph/file/f906b4fa707c626e4dc6b.jpg https://te.legra.ph/file/6d4f83a7cda4f10e2b3b2.jpg https://te.legra.ph/file/072ef650b4b2d5a49a503.jpg https://te.legra.ph/file/039d4bc3584465dd5fca1.jpg https://te.legra.ph/file/f4e6b030d272df1014238.jpg https://te.legra.ph/file/f05394443a3d28f2a4c14.jpg https://te.legra.ph/file/efc1f531f3b8e9ff230c3.jpg https://te.legra.ph/file/c9bdd39ea9101292e3cf2.jpg https://te.legra.ph/file/2f3d7484a476a6cd830d2.jpg https://te.legra.ph/file/200ccdee16992bfbcaa34.jpg https://te.legra.ph/file/68eedaaa4719bc5d9c4ad.jpg https://te.legra.ph/file/e9c994771bd2fa642bd05.jpg https://te.legra.ph/file/afce0288e7ae954d0851b.jpg https://te.legra.ph/file/a0984dd4e35c5f7bf570e.jpg https://te.legra.ph/file/6b03c36f89498e005220e.jpg https://te.legra.ph/file/48c3d0428c80ff565d5bf.jpg https://te.legra.ph/file/b94d1c3a0fa99369d90e7.jpg https://te.legra.ph/file/89ce32261fc775ef5e325.jpg https://te.legra.ph/file/be1ab57f0451cea324874.jpg https://te.legra.ph/file/665664044aa53a5331ae3.jpg https://te.legra.ph/file/5d6c2f2ecdaaecf59e308.jpg https://te.legra.ph/file/0a2ac5d0d6c6e88a60a20.jpg https://te.legra.ph/file/5410e07d5207d341a835b.jpg https://te.legra.ph/file/518001fcc0fbed6ee4fda.jpg https://te.legra.ph/file/699c11b1b1d1ac319ee39.jpg https://te.legra.ph/file/535313683e0af107094c3.jpg https://te.legra.ph/file/52466fd7632e09a14dd11.jpg https://te.legra.ph/file/ba95107c0368633ab3eca.jpg https://te.legra.ph/file/80199cad9e34479e07f9c.jpg https://te.legra.ph/file/9a1bccfcc4c2ce8e38f0f.jpg https://te.legra.ph/file/da76a5805099b5d062ded.jpg https://te.legra.ph/file/cf79fc9511fe8860909b1.jpg https://te.legra.ph/file/b232ecbaa24db68b01769.jpg https://te.legra.ph/file/3367383afa3cb650080d4.jpg https://te.legra.ph/file/4ed9edda92b1df712d88e.jpg https://te.legra.ph/file/4d2fcd419903280ac26b9.jpg https://te.legra.ph/file/fa6e8ed291f5d9f2a809e.jpg https://te.legra.ph/file/de376ed7fa56c29668a8c.jpg https://te.legra.ph/file/539448e0f19b9a8952f9c.jpg https://te.legra.ph/file/64b1f1ba5e179ca7d74b1.jpg https://te.legra.ph/file/87248cbd08390b960f4d4.jpg https://te.legra.ph/file/fb764ecc977dd0e6670b4.jpg https://te.legra.ph/file/2979825d0c1c0637a69d2.jpg https://te.legra.ph/file/8429ae6a630cdf572511f.jpg https://te.legra.ph/file/013967f7a908ca70f13cc.jpg https://te.legra.ph/file/046b58a922c075e130f75.jpg https://te.legra.ph/file/c30c379b415c708267c2c.jpg https://te.legra.ph/file/1d2ef52aec7bff9651995.jpg https://te.legra.ph/file/5bf1e2dcc3101fb1acdad.jpg https://te.legra.ph/file/93a2d11987d6b10636f6d.jpg https://te.legra.ph/file/1e3274e326a108e2c251a.jpg https://te.legra.ph/file/bc6c3256f0ca870dff122.jpg https://te.legra.ph/file/5ad5112688fb9494edc5c.jpg https://te.legra.ph/file/9ec0a2ac4db16f9754c13.jpg https://te.legra.ph/file/792ee58219005abccfa30.jpg https://te.legra.ph/file/ecf5d8e6d814ab380afd6.jpg https://te.legra.ph/file/e7e228d5cda8f20b65659.jpg https://te.legra.ph/file/7da790a19377f241dd141.jpg https://te.legra.ph/file/d068086a4e6a8034ab357.jpg https://te.legra.ph/file/970c6d6d82f396e127134.jpg https://te.legra.ph/file/f7c4c2e1984418a0beaa6.jpg https://te.legra.ph/file/90dc9f5c995275cde9901.jpg https://te.legra.ph/file/c5e005551d5cf28d6fe88.jpg https://te.legra.ph/file/f265edb227e66fac9395d.jpg https://te.legra.ph/file/9a178ba1ef0ab3281c003.jpg https://te.legra.ph/file/62d7943bdae08f3591479.jpg https://te.legra.ph/file/c34f4fc2f3db4c366edf3.jpg https://te.legra.ph/file/14fd08f28dd28e7336069.jpg https://te.legra.ph/file/8a970868eb31f60a03f40.jpg https://te.legra.ph/file/4db202d5ce66f2bf83978.jpg https://te.legra.ph/file/dc67f22f9bdf62b2d1212.jpg https://te.legra.ph/file/c93017d6ae7431410b3a6.jpg https://te.legra.ph/file/1854b0f8401a9627277e5.jpg https://te.legra.ph/file/eb4465ca1f1f1b870a99d.jpg https://te.legra.ph/file/5e58d9547563c6008a24c.jpg https://te.legra.ph/file/5513a0372680c9367b467.jpg https://te.legra.ph/file/b8dffb8f32929c3981964.jpg https://te.legra.ph/file/289ffa2e8d8d46ad74f93.jpg https://te.legra.ph/file/5bb23a840e2e33f3f4f04.jpg https://te.legra.ph/file/5de96fb1bb96f3bb8ca02.jpg https://te.legra.ph/file/c374cb1bbf199485eb3f5.jpg https://te.legra.ph/file/e9d9ed8e3bfe9490d47ca.jpg https://te.legra.ph/file/ada7a1c3921baec8831c9.jpg https://te.legra.ph/file/902446c964e35456f1909.jpg https://te.legra.ph/file/c04f65d0ad064973b343b.jpg https://te.legra.ph/file/cf4c5ee682070346b092d.jpg https://te.legra.ph/file/71f3123665de95783cffb.jpg https://te.legra.ph/file/1bebacc80923abe2bd48c.jpg https://te.legra.ph/file/8eafc17f739ca84ef74f1.jpg https://te.legra.ph/file/6a9b86acd6f5bdacd5d5e.jpg https://te.legra.ph/file/07e174d10a80589a988dc.jpg https://te.legra.ph/file/b8819507fa0460d11067d.jpg https://te.legra.ph/file/ddb3f07199fd33d9e5c80.jpg https://te.legra.ph/file/7064e87f9e568b11c3d8c.jpg https://te.legra.ph/file/0cbd504f3214fe218ae07.jpg https://te.legra.ph/file/2ce3935ac2c7d19e8284c.jpg https://te.legra.ph/file/50167b8ac83ab2e9b6c53.jpg https://te.legra.ph/file/2059dbf7d86bcd3617f9b.jpg https://te.legra.ph/file/70cd0706c99c801d07e76.jpg https://te.legra.ph/file/1b0982254e21ca5ec70f1.jpg https://te.legra.ph/file/028eb692d352b1ad6f024.jpg https://te.legra.ph/file/7665b5bf18ff94213a86c.jpg https://te.legra.ph/file/1c19804643ba06d392bd4.jpg https://te.legra.ph/file/1ba1d5cfc07ca46913693.jpg https://te.legra.ph/file/0b7f4041873c4bd5749dd.jpg https://te.legra.ph/file/0d31a927b81234368aa80.jpg https://te.legra.ph/file/ad7cb0a6861cc180e77cb.jpg https://te.legra.ph/file/7dc3eac027f4bec089fd9.jpg https://te.legra.ph/file/193c509f482d3e212edde.jpg https://te.legra.ph/file/3e609e8f2e6c94ff4f6c5.jpg https://te.legra.ph/file/e14905bb7b4fdf65a78d0.jpg https://te.legra.ph/file/42cd02b4ec9b16a7b1cdf.jpg https://te.legra.ph/file/bd1cc3b74fff34e0b5a96.jpg https://te.legra.ph/file/4c266cee312282c294c8f.jpg https://te.legra.ph/file/328c76b07f107a02ae9b0.jpg https://te.legra.ph/file/c93566ee2c6b646f32d99.jpg https://te.legra.ph/file/1fcc912ce3ff4076d4d9f.jpg https://te.legra.ph/file/f6f15115c87adb3eb2514.jpg https://te.legra.ph/file/ad81a17c3dc5508fe7e5a.jpg https://te.legra.ph/file/0718f90673f5eb7285fad.jpg https://te.legra.ph/file/af0bac660d7e7d618f1c5.jpg https://te.legra.ph/file/e58e4ea2f24495803f52a.jpg https://te.legra.ph/file/0fd9b75a286481bd66d5d.jpg https://te.legra.ph/file/9b417f80ec9e429150f90.jpg https://te.legra.ph/file/17ec6ffb8da201f6d0c09.jpg https://te.legra.ph/file/a7357dc340f443d6e0c80.jpg https://te.legra.ph/file/7b125fa6ec4841dc244e8.jpg https://te.legra.ph/file/7c3e7017231666c6764ff.jpg https://te.legra.ph/file/cafb1be4153c9464c877b.jpg https://te.legra.ph/file/0d393db406ea81f5ea112.jpg https://te.legra.ph/file/38e2374f0b5da9b4f8447.jpg https://te.legra.ph/file/7ee8305bd674c8c3d0815.jpg https://te.legra.ph/file/fc229d3e4a72952c46ed4.jpg https://te.legra.ph/file/15062fd7e7faa249699dd.jpg https://te.legra.ph/file/77d95d7fe94cb3049974a.jpg https://te.legra.ph/file/14ac6148bbf9741c4f314.jpg https://te.legra.ph/file/66617909b473f34356621.jpg https://te.legra.ph/file/7a34b2e4d928b78f31fd0.jpg https://te.legra.ph/file/d545dddd9c0d57e374697.jpg https://te.legra.ph/file/d3cfb4bc5dc58491f420b.jpg https://te.legra.ph/file/c1003c011e9e8fe003893.jpg https://te.legra.ph/file/fa26722acae6e4d0e34a2.jpg https://te.legra.ph/file/ac4ac8382916d0af1e55f.jpg https://te.legra.ph/file/290d6b4fd3d1b4f9c3c1f.jpg https://te.legra.ph/file/5c388d6650afd603cafcb.jpg https://te.legra.ph/file/0871bf70eef8f670a9168.jpg https://te.legra.ph/file/97ea04cb019bb25b0b381.jpg https://te.legra.ph/file/f16a5c13c38874eca78bb.jpg https://te.legra.ph/file/21cd623a37b6cf54c2f42.jpg https://te.legra.ph/file/af89931b3c79dd8d9a1d1.jpg https://te.legra.ph/file/f7d6799fe5682f8b80a22.jpg https://te.legra.ph/file/5e8d3c042e2be052412e9.jpg https://te.legra.ph/file/12ac0f64b11804f9d99f0.jpg https://te.legra.ph/file/04cbd3545e3f58460570a.jpg https://te.legra.ph/file/f74fd2a8abac9aa3763c9.jpg https://te.legra.ph/file/1eb5c944488fd40966f27.jpg https://te.legra.ph/file/bf705f7a1d4d92fd364ee.jpg https://te.legra.ph/file/dad7e447fb452233dbfc6.jpg https://te.legra.ph/file/3f1b64a8236cc6723f365.jpg https://te.legra.ph/file/10dbce7e46e58e1c32f80.jpg https://te.legra.ph/file/f2187ac6c93bd6c1ed6c2.jpg https://te.legra.ph/file/48fa7b86fbbf753996635.jpg https://te.legra.ph/file/c3cd6b3f2626d2e4d315a.jpg https://te.legra.ph/file/3f33b66ac9a89235bd0e7.jpg https://te.legra.ph/file/3fdcda9c9ad1f85203a81.jpg https://te.legra.ph/file/213024d0475f75f6b3a51.jpg https://te.legra.ph/file/d5c640c91ea06878de423.jpg https://te.legra.ph/file/cc57008e5542b2b2b5d83.jpg https://te.legra.ph/file/b8f43055060b3af1305de.jpg https://te.legra.ph/file/b6ddc07460e8bb99a6269.jpg https://te.legra.ph/file/f514d2d18863497674cea.jpg https://te.legra.ph/file/1977e5a9e499da7611cea.jpg https://te.legra.ph/file/cdf0f7cfe9f5043d985c7.jpg https://te.legra.ph/file/49dc1ccc13a9b69d7e662.jpg https://te.legra.ph/file/869f13333f3bb9fe757a3.jpg https://te.legra.ph/file/a6ed22cf9089c835dc9c1.jpg https://te.legra.ph/file/43202c6ba9f6fa4c5adc3.jpg https://te.legra.ph/file/6e148e34cf85f05221afd.jpg https://te.legra.ph/file/5d0dcc25c2737df7966b8.jpg https://te.legra.ph/file/3bf6997996fda01dd93f1.jpg https://te.legra.ph/file/3d3f4bd8a65a5b9dc51c5.jpg https://te.legra.ph/file/91f639eaa18dae8458db2.jpg https://te.legra.ph/file/b8982e7515a56dad72f89.jpg https://te.legra.ph/file/d55d384d17d30e3332b14.jpg https://te.legra.ph/file/1f032d9ab913fc5ba4cb2.jpg https://te.legra.ph/file/20b1c726badf78ec5b948.jpg https://te.legra.ph/file/d51344188dec5716ff237.jpg https://te.legra.ph/file/aa125aaf7187910132a4d.jpg https://te.legra.ph/file/57c7a84278fc7660ca453.jpg https://te.legra.ph/file/d9701a7a06d5a9efaafdc.jpg https://te.legra.ph/file/7109687101280a37fdeca.jpg https://te.legra.ph/file/ad5e758e5bef19cb316d6.jpg https://te.legra.ph/file/790eb8dccec3722281daf.jpg https://te.legra.ph/file/9ddc4190e9103e039011c.jpg https://te.legra.ph/file/66465749547c077b6e93e.jpg https://te.legra.ph/file/4436ec34f4c4feaadef39.jpg https://te.legra.ph/file/7cd1470f5eb9d6e7d89db.jpg https://te.legra.ph/file/9b26f37008672cc94d5e2.jpg https://te.legra.ph/file/ca4492bbf75940211f20c.jpg https://te.legra.ph/file/3d7e6f4debc4052ec37e2.jpg https://te.legra.ph/file/ed1025e412d3ac120d44b.jpg https://te.legra.ph/file/8225ba6451b0f351b3fe8.jpg https://te.legra.ph/file/105f83c7aafeac4da7dd2.jpg https://te.legra.ph/file/b6be5c94cc158907a1d94.jpg https://te.legra.ph/file/db15c3aada86c4c0d0e6f.jpg https://te.legra.ph/file/05d831e69f64f2942227c.jpg https://te.legra.ph/file/93f7dd7b2dd79184bb91e.jpg https://te.legra.ph/file/d97727fea796eb7f76b15.jpg https://te.legra.ph/file/e310db45af36a599e33c6.jpg https://te.legra.ph/file/8bf6d5d8ce28e40a7f23a.jpg https://te.legra.ph/file/f290729280f1d1365a1f8.jpg https://te.legra.ph/file/8216759190efdae718786.jpg https://te.legra.ph/file/01eb42eb49be6c0dea6f0.jpg https://te.legra.ph/file/3466ed1b9e2d33e1198c4.jpg https://te.legra.ph/file/9106fb2e79fa356327d0e.jpg https://te.legra.ph/file/a0f126abde88b9c31bbfc.jpg https://te.legra.ph/file/b125b855d8c2ccbac9bef.jpg https://te.legra.ph/file/40a3f86d7a36612a6c00e.jpg https://te.legra.ph/file/c9e1984ee73453506a620.jpg https://te.legra.ph/file/74a6fab8ba3b47be5f734.jpg https://te.legra.ph/file/c40e472055ef2ef2cf28f.jpg https://te.legra.ph/file/e5a19e5e233324e031c33.jpg https://te.legra.ph/file/df0a2227d31dd76ba950a.jpg https://te.legra.ph/file/3f82c16d99de731492b7c.jpg https://te.legra.ph/file/a9ef73a2246294798cb40.jpg https://te.legra.ph/file/4b276b5d11528c700924b.jpg https://te.legra.ph/file/c69c9643e5d580b693631.jpg https://te.legra.ph/file/99cb4c78b3f78d26d8b98.jpg https://te.legra.ph/file/0af736f84c4f97b348286.jpg https://te.legra.ph/file/491a5ebfaa3dd5402a51e.jpg https://te.legra.ph/file/b7b413a1a87fa4b5dd55e.jpg https://te.legra.ph/file/92ea4bf4044964e52353e.jpg https://te.legra.ph/file/bf394c5743dc1d246ecb9.jpg https://te.legra.ph/file/200ce6d8d626adf58fb01.jpg https://te.legra.ph/file/4e996f5007883ebc24509.jpg https://te.legra.ph/file/cf105bf07cb8a0d8e67ae.jpg https://te.legra.ph/file/b4dba40630d18674830da.jpg https://te.legra.ph/file/c73c2d86f896adc0e1769.jpg https://te.legra.ph/file/9b55b64c7d0e36858acc9.jpg https://te.legra.ph/file/47a156e816282d752090d.jpg https://te.legra.ph/file/1fe8dd012b3cddbce8ea8.jpg https://te.legra.ph/file/f67879b463a261fc3a030.jpg https://te.legra.ph/file/15e2b01c46a6b2756135d.jpg https://te.legra.ph/file/16abad8604e7beba65e0f.jpg https://te.legra.ph/file/85c21e6c9519dbf357159.jpg https://te.legra.ph/file/503ec332eabdffae42323.jpg https://te.legra.ph/file/b6734c69b892760e2e20a.jpg https://te.legra.ph/file/ea216b9725cb17d9c282d.jpg https://te.legra.ph/file/740b81c4c724ed3c7ff93.jpg https://te.legra.ph/file/4c15626f856dd5c1af1ec.jpg https://te.legra.ph/file/0ad72da45789feff6a9df.jpg https://te.legra.ph/file/419b331c647b8de9a5d05.jpg https://te.legra.ph/file/668a519e846470da05a01.jpg https://te.legra.ph/file/fee4c52f3b727bebdb3cd.jpg https://te.legra.ph/file/fc42b05e5fd98fadf35a8.jpg https://te.legra.ph/file/df4bdeab32240c25c1ef1.jpg https://te.legra.ph/file/67c91980336edcadc0a84.jpg https://te.legra.ph/file/51bf0fe4d69b7c50209b9.jpg https://te.legra.ph/file/076569f12a1e3e5b3fcef.jpg https://te.legra.ph/file/5b597279057ecf48002ed.jpg https://te.legra.ph/file/fe79de00efbf2cb754899.jpg https://te.legra.ph/file/be3fca1640e65a849bea3.jpg https://te.legra.ph/file/4124ab26ffbc493ee553a.jpg https://te.legra.ph/file/bfb03e68de9fba9ead40b.jpg https://te.legra.ph/file/29254edac5c97ca7f10bb.jpg https://te.legra.ph/file/ef291a011886d36d60a4f.jpg https://te.legra.ph/file/f20f4a4254d4afeabe737.jpg https://te.legra.ph/file/65219a6fc5ae3278a5788.jpg https://te.legra.ph/file/bf81afd5568b5db109633.jpg https://te.legra.ph/file/ca710f15e16e8a51a077f.jpg https://te.legra.ph/file/046ae4b92f03ad5c0d02e.jpg https://te.legra.ph/file/6ee9caec312436c1d56d4.jpg https://te.legra.ph/file/c6a1855a7ff78c91955f6.jpg https://te.legra.ph/file/40567e1a3d034c9643587.jpg https://te.legra.ph/file/20175463b1e86036e9bbc.jpg https://te.legra.ph/file/a34f05ecda1d24597b110.jpg https://te.legra.ph/file/add3dca83a193f19f1f93.jpg https://te.legra.ph/file/4fb0d3c872da2915c71a8.jpg https://te.legra.ph/file/29acf675e8c91889d877d.jpg https://te.legra.ph/file/4b7e4e40c9b29b9b976c4.jpg https://te.legra.ph/file/1e3688fe772e89c099538.jpg https://te.legra.ph/file/bf8abf3877e1a725c0053.jpg https://te.legra.ph/file/cda14b290de2e0b8b23ff.jpg https://te.legra.ph/file/1aa4a7c47b56f40b578d7.jpg https://te.legra.ph/file/4b5e0ebe4a756a9669bd8.jpg https://te.legra.ph/file/d7a97faa1104b1d31ac10.jpg https://te.legra.ph/file/d07659b71ebe5550d14b7.jpg https://te.legra.ph/file/60021c78e797604e5c624.jpg https://te.legra.ph/file/c0de540030e91b6f45b81.jpg https://te.legra.ph/file/0d73466015863837d55c4.jpg https://te.legra.ph/file/0db9470e1f4e3a76521ac.jpg https://te.legra.ph/file/ae7d6655c9dc06e881358.jpg https://te.legra.ph/file/02fad99f89672e7b293dd.jpg https://te.legra.ph/file/beae0a1cd324249506106.jpg https://te.legra.ph/file/a15048624d139bbc8f6d6.jpg https://te.legra.ph/file/e0f338b40e7d8e13e9e32.jpg https://te.legra.ph/file/59b0567ddec02fd4d59cc.jpg https://te.legra.ph/file/31ec000a1afedb7a50a85.jpg https://te.legra.ph/file/b1e5645bed027b83f217c.jpg https://te.legra.ph/file/56779e203f56aabe1ea1e.jpg https://te.legra.ph/file/655deb5be63d5ff10ab69.jpg https://te.legra.ph/file/28d0924a48a7df7d8ce3f.jpg https://te.legra.ph/file/1c465de1dbe5cf706f9ad.jpg https://te.legra.ph/file/a913d071e4f062c57382a.jpg https://te.legra.ph/file/1de3f8413f6525da8ea2a.jpg https://te.legra.ph/file/828859b339892047ec557.jpg https://te.legra.ph/file/233b744aa2530f294e459.jpg https://te.legra.ph/file/8624a16fb15bfaa184f4a.jpg https://te.legra.ph/file/4c34d49b190e33679b05e.jpg https://te.legra.ph/file/30ec1032f30e174ae3a69.jpg https://te.legra.ph/file/806be3632d2b959de272a.jpg https://te.legra.ph/file/381605797c5f271790a06.jpg https://te.legra.ph/file/e95bc82a82987e6714843.jpg https://te.legra.ph/file/1aae773539280af45c2e4.jpg https://te.legra.ph/file/7651a994773fdf4d5ee54.jpg https://te.legra.ph/file/48a8344752436f9730a4f.jpg https://te.legra.ph/file/5d90a7a608467ff0b64d9.jpg https://te.legra.ph/file/a759941769497217b5735.jpg https://te.legra.ph/file/16e0e4b0595be468559d8.jpg https://te.legra.ph/file/4f1eb7bce84dcc5ac1f3d.jpg https://te.legra.ph/file/a0d27dc7262cde6da4992.jpg https://te.legra.ph/file/c9eb081e403aaab079a29.jpg https://te.legra.ph/file/28a53490f71f9892054ec.jpg https://te.legra.ph/file/e903ff4cfad05698db966.jpg https://te.legra.ph/file/575b586939721cbc25c71.jpg https://te.legra.ph/file/45542ec6c51d7dcc64d2f.jpg https://te.legra.ph/file/77843a025036f9f0ad41f.jpg https://te.legra.ph/file/de97ac0f648dbe829c63e.jpg https://te.legra.ph/file/9d64258a72874ee90f612.jpg https://te.legra.ph/file/29c227f0d3c534ac060a7.jpg https://te.legra.ph/file/10ea6209f07e9a9e9a31d.jpg https://te.legra.ph/file/93289d6b1987a273cb890.jpg https://te.legra.ph/file/acc6aedbad98fa3831703.jpg https://te.legra.ph/file/7b7c744dfe7ffa4efa10f.jpg https://te.legra.ph/file/a3b2a5aebf2e6a02312f6.jpg https://te.legra.ph/file/e982816a10b5fe747d59e.jpg https://te.legra.ph/file/0a66d4a0e96509f63919c.jpg https://te.legra.ph/file/6d5bd12b614d6e77256d5.jpg https://te.legra.ph/file/e6690a0fbc5b1350e5ea9.jpg https://te.legra.ph/file/8aa6f02b319e54b56e092.jpg https://te.legra.ph/file/ee5b053d049ca707964a0.jpg https://te.legra.ph/file/ff2fe9ae18178a1f60424.jpg https://te.legra.ph/file/5f25dfceafb96d2cf69a1.jpg https://te.legra.ph/file/4dfe3a64e5978901952fa.jpg https://te.legra.ph/file/6c80ac7328f988f6ea9db.jpg https://te.legra.ph/file/353de4b4eca985adc0496.jpg https://te.legra.ph/file/3939daac451cc43c76484.jpg https://te.legra.ph/file/a5358cee50324cbfa7c23.jpg https://te.legra.ph/file/e6891f59ce5bfc6fdda69.jpg https://te.legra.ph/file/efb0ea45b46f09f02a5ea.jpg https://te.legra.ph/file/9ce89861439c4ac39d3b3.jpg https://te.legra.ph/file/6a9788dee75a3d5765f04.jpg https://te.legra.ph/file/72ced54b304ebff34573b.jpg https://te.legra.ph/file/e00d80606a868801f484a.jpg https://te.legra.ph/file/f9f01df298273301576a0.jpg https://te.legra.ph/file/a9445b1ed19400392b894.jpg https://te.legra.ph/file/7d2295e5ad508de05d5b6.jpg https://te.legra.ph/file/a436565d5d52aaff0240d.jpg https://te.legra.ph/file/1e880f8af742975d99bcd.jpg https://te.legra.ph/file/b8ac968e0b3ec424edac7.jpg https://te.legra.ph/file/b8c7dfcc79bea3c38a3d7.jpg https://te.legra.ph/file/dcbce83cfa6fcf97d2c7a.jpg https://te.legra.ph/file/32f2037503d3a7f6e136f.jpg https://te.legra.ph/file/b50bfdcaf73186660bf4e.jpg https://te.legra.ph/file/27daa6b4d37352a39a0b4.jpg https://te.legra.ph/file/ba94ce9e41327f4b3c326.jpg https://te.legra.ph/file/6dd0e346066b0f39fe745.jpg https://te.legra.ph/file/0e5f1120e88e4070c802a.jpg https://te.legra.ph/file/88969ce18964fbd2098ef.jpg https://te.legra.ph/file/9a9bd1f3ba158d6795bad.jpg https://te.legra.ph/file/98e4361c2616d695dab88.jpg https://te.legra.ph/file/98bcc7214bf35606fa7f9.jpg https://te.legra.ph/file/aa5390989186eaaa742a5.jpg https://te.legra.ph/file/d7dcf3caca446c8a653c5.jpg https://te.legra.ph/file/ec13c0327c5428c1fdf82.jpg https://te.legra.ph/file/3437e7c3467d738ceada3.jpg https://te.legra.ph/file/096f851fa5dbd2f53f7d3.jpg https://te.legra.ph/file/53ddae963693366c96efe.jpg https://te.legra.ph/file/e9e3dac9640ef78269c25.jpg https://te.legra.ph/file/ab982b8591f9d31958470.jpg https://te.legra.ph/file/5ad352714a22ec67e7543.jpg https://te.legra.ph/file/a73893de8b791ad39e632.jpg https://te.legra.ph/file/a60ac342539fd9732d81d.jpg https://te.legra.ph/file/34a25ba8a2388f5f8222f.jpg https://te.legra.ph/file/b596cab15516ed1b05af8.jpg https://te.legra.ph/file/e20d258115d8350826b01.jpg https://te.legra.ph/file/00d644de7a778c084f2af.jpg https://te.legra.ph/file/9a3ef1462d5331a23c9a1.jpg https://te.legra.ph/file/fe7fa4619cea2bd37be53.jpg https://te.legra.ph/file/254919c9b7fce0c65a7a7.jpg https://te.legra.ph/file/dac75e2b76366421dddbe.jpg https://te.legra.ph/file/21dc36fdc205e8c8ffb16.jpg https://te.legra.ph/file/04a49511c13f8cf5086a3.jpg https://te.legra.ph/file/75b1d4c03c7163d46d921.jpg https://te.legra.ph/file/6f96eda79fd6c5b64ef1c.jpg https://te.legra.ph/file/e589711cb8d67f3093a8d.jpg https://te.legra.ph/file/38cd433a3fad536c0853b.jpg https://te.legra.ph/file/814f7d51b1cf6c3ff575e.jpg https://te.legra.ph/file/0e2f096f7e90f313e4212.jpg https://te.legra.ph/file/39cd85135d93b3c5a3cad.jpg https://te.legra.ph/file/9c6b3c34a6e6cd3317cd0.jpg https://te.legra.ph/file/abf90ac5206fcec9b6467.jpg https://te.legra.ph/file/8a5db71aafc185b5cf2e9.jpg https://te.legra.ph/file/b83c82ef44912b86c4224.jpg https://te.legra.ph/file/b16c179d282b4925afaca.jpg https://te.legra.ph/file/dd469713be2d005258e0e.jpg https://te.legra.ph/file/deb50a8cb41c900fc1617.jpg https://te.legra.ph/file/c08819d52ebf42103e611.jpg https://te.legra.ph/file/0d0589b280ef43a5f740c.jpg https://te.legra.ph/file/1fec0e723c66efe1d2155.jpg https://te.legra.ph/file/018629ce993f72bfb1e6a.jpg https://te.legra.ph/file/195ffa940ddddfa5e0a85.jpg https://te.legra.ph/file/88f49ee68a12aa1da66ae.jpg https://te.legra.ph/file/19d54de5ac1b875b3d381.jpg https://te.legra.ph/file/701586048bb72409c99b4.jpg https://te.legra.ph/file/f2bea9e4e527e542b45b1.jpg https://te.legra.ph/file/f798c99942968cc78d0a5.jpg https://te.legra.ph/file/a803d80a70147f2112495.jpg https://te.legra.ph/file/b4c3ff5a950d16f3d4c9a.jpg https://te.legra.ph/file/8681a113107969b3ec9ff.jpg https://te.legra.ph/file/06c182cf394780278fda1.jpg https://te.legra.ph/file/d21e632216f94171fa557.jpg https://te.legra.ph/file/f66883453ea99a62e2e36.jpg https://te.legra.ph/file/e9cd104a0357ad97e6d19.jpg https://te.legra.ph/file/e529cb63757441244d492.jpg https://te.legra.ph/file/d5ac275bd070b712c1b19.jpg https://te.legra.ph/file/75695d45c8864c03eb43c.jpg https://te.legra.ph/file/aea7add8e1dc8b5b080b6.jpg https://te.legra.ph/file/e6f0e6580845108fea76a.jpg https://te.legra.ph/file/92db5b14540b6032862a5.jpg https://te.legra.ph/file/9a814f1e11bbd16137c28.jpg https://te.legra.ph/file/b6a96fd62c893130278dc.jpg https://te.legra.ph/file/cce6fe9571e799f6cd2f7.jpg https://te.legra.ph/file/8ad41f5c4d1b9f325f1ec.jpg https://te.legra.ph/file/c5bfb8bd3e7cd907a52fb.jpg https://te.legra.ph/file/dcca8760a3e1d7990513c.jpg https://te.legra.ph/file/20bb8cc9b9b83e933ad0a.jpg https://te.legra.ph/file/636082b7971f4cdc866c4.jpg https://te.legra.ph/file/f1829fed6002c2c513de7.jpg https://te.legra.ph/file/6104a3a4e349d79b9b1da.jpg https://te.legra.ph/file/13d87c2cdb5caa57d993f.jpg https://te.legra.ph/file/2f9c55d3907dc92445c4a.jpg https://te.legra.ph/file/0b3b1d9109c7641499cb5.jpg https://te.legra.ph/file/552c845941b5ef2fb3254.jpg https://te.legra.ph/file/1240ba3fc7dc1f333b9aa.jpg https://te.legra.ph/file/4ea6a9d979ec2fc3f8716.jpg https://te.legra.ph/file/d9e839d20f68e2781f84f.jpg https://te.legra.ph/file/89526b9969a67983da045.jpg https://te.legra.ph/file/13bb27bf1c6f08990ef67.jpg https://te.legra.ph/file/78af40ac95d03aaf5c086.jpg https://te.legra.ph/file/1120246bf9850fd2dc38f.jpg https://te.legra.ph/file/3bb597498febc70205299.jpg https://te.legra.ph/file/7717204c938ee8465ed21.jpg https://te.legra.ph/file/b8492e9562158e310633f.jpg https://te.legra.ph/file/d95257500593d08ba62db.jpg https://te.legra.ph/file/727c3686b1d05dea42cb0.jpg https://te.legra.ph/file/be045ff9300d08d58c437.jpg https://te.legra.ph/file/cbf79809b9d200d0bfdf9.jpg https://te.legra.ph/file/daaf1c51897953a82c905.jpg https://te.legra.ph/file/02cd5d0000c2b343e36ab.jpg https://te.legra.ph/file/46956355f7a70f8847453.jpg https://te.legra.ph/file/85741c12a083ca2d24e80.jpg https://te.legra.ph/file/0d5a491b7dcc719960d8d.jpg https://te.legra.ph/file/ab51e5cea2f3ff1bc31a6.jpg https://te.legra.ph/file/c4886ce25bf32fb65a6b0.jpg https://te.legra.ph/file/345997f14e64a26395f73.jpg https://te.legra.ph/file/3d3fc8d7de53a49ad26a6.jpg https://te.legra.ph/file/8da8852d264b7f873f3a0.jpg https://te.legra.ph/file/de628b2860b8754927e2c.jpg https://te.legra.ph/file/f0f2a90fa105de687b3b6.jpg https://te.legra.ph/file/4cdb15ef2e5d0bacdf2a4.jpg https://te.legra.ph/file/01a092afb70968af98a7f.jpg https://te.legra.ph/file/c83af896a10967c84ab11.jpg https://te.legra.ph/file/2767dedf2c4bed595c6f1.jpg https://te.legra.ph/file/b3a57672b08dd7fd90606.jpg https://te.legra.ph/file/3b12dadb33e8862032be5.jpg https://te.legra.ph/file/ffcd2ba2321c19e948ee3.jpg https://te.legra.ph/file/7062051371c864beabc61.jpg https://te.legra.ph/file/9af3f7ec560ed8bb34db1.jpg https://te.legra.ph/file/abbe70571d449dc673ac7.jpg https://te.legra.ph/file/70c928f965fa5ef5ec7ab.jpg https://te.legra.ph/file/6a1dbd91949be232b6670.jpg https://te.legra.ph/file/a1f84586fb6fd3f095e88.jpg https://te.legra.ph/file/d4b2184af5adff9bbf173.jpg https://te.legra.ph/file/40a4c946257a61f744881.jpg https://te.legra.ph/file/59931ca62a356563c58eb.jpg https://te.legra.ph/file/0bb052660a20669f18751.jpg https://te.legra.ph/file/5cb3f7044a3e4c8855185.jpg https://te.legra.ph/file/5fe54867812723555f59f.jpg https://te.legra.ph/file/d128c1b3aaca37cc2aac7.jpg https://te.legra.ph/file/341b70315070ab6b741ba.jpg https://te.legra.ph/file/f625c369e937e36573df0.jpg https://te.legra.ph/file/9e276421a9d7aae474d20.jpg https://te.legra.ph/file/79323f85a40fc5b250a47.jpg https://te.legra.ph/file/26f8d94fc47bcff3e5bdd.jpg https://te.legra.ph/file/a8b07a945539ac3ff0c45.jpg https://te.legra.ph/file/b40888c9ad1de7d45db70.jpg https://te.legra.ph/file/337f0e75169549d9ee489.jpg https://te.legra.ph/file/dcd1ed234b60026e6084b.jpg https://te.legra.ph/file/d42ade18c81280045d9c7.jpg https://te.legra.ph/file/7d8d02f588a90ebe6a2e8.jpg https://te.legra.ph/file/593e327ac3afba0d2060e.jpg https://te.legra.ph/file/a5137c70dd1361532735f.jpg https://te.legra.ph/file/3300653b3a041dd9202b0.jpg https://te.legra.ph/file/30fb36ca5f87ca3c950d4.jpg https://te.legra.ph/file/9b73e21f4d565fea64372.jpg https://te.legra.ph/file/74bb4c127faf075a8d996.jpg https://te.legra.ph/file/72cd706243ff8239057e8.jpg https://te.legra.ph/file/7b2f0038d8f82dd1b59d6.jpg https://te.legra.ph/file/a5b0d1273c58c515b4c03.jpg https://te.legra.ph/file/6451a3ef95f5a549c10fb.jpg https://te.legra.ph/file/88361a3921254da11beaa.jpg https://te.legra.ph/file/43c8c6ffbf5f4e7f1c096.jpg https://te.legra.ph/file/c1d839789e3f987d9d006.jpg https://te.legra.ph/file/e7f30e7ac7aa55fe9722b.jpg https://te.legra.ph/file/021ea5562ed1f9aa361ef.jpg https://te.legra.ph/file/0b440856d2a0556c06da1.jpg https://te.legra.ph/file/814660712bd8fabc6d3cd.jpg https://te.legra.ph/file/d0874552f051431a9469e.jpg https://te.legra.ph/file/9cb2693dee93891f368bc.jpg https://te.legra.ph/file/d18af2bff5f5b747231ac.jpg https://te.legra.ph/file/15344c1ba6aaddf5ceb50.jpg https://te.legra.ph/file/28e4e6b58a9b44b1e17ff.jpg https://te.legra.ph/file/a188e7cb4cdc12450cd62.jpg https://te.legra.ph/file/46bee8932ef62047dfd61.jpg https://te.legra.ph/file/8ea56b5e5e33691938683.jpg https://te.legra.ph/file/bd3a924b5a7a397df0be0.jpg https://te.legra.ph/file/979b1a58e516f6a8a783e.jpg https://te.legra.ph/file/4d4efad3b2ee32933debb.jpg https://te.legra.ph/file/a542a9722ff0af1f244e5.jpg https://te.legra.ph/file/352bc903bd2d3135138c1.jpg https://te.legra.ph/file/d8782466103727214e3d4.jpg https://te.legra.ph/file/116ea29653d7d13b1d528.jpg https://te.legra.ph/file/907839fbd9c0e89a01387.jpg https://te.legra.ph/file/21de4d5dbef433f6b3628.jpg https://te.legra.ph/file/ed1ce02f76ec52ec58bed.jpg https://te.legra.ph/file/09dddd6fa686018f4d8ee.jpg https://te.legra.ph/file/0fdc30860e270eeedf4b4.jpg https://te.legra.ph/file/6967e2ffdc6610a90c273.jpg https://te.legra.ph/file/2ebba7c38ced989006b40.jpg https://te.legra.ph/file/fd5a22801543ffa9ec792.jpg https://te.legra.ph/file/d7ca7c2c46b3b868538dd.jpg https://te.legra.ph/file/2e04e9b96a86cebba9d80.jpg https://te.legra.ph/file/dcf4a2fd09b7de3527b75.jpg https://te.legra.ph/file/7482639c7555a2bfea849.jpg https://te.legra.ph/file/f97cac5573bc67bc979af.jpg https://te.legra.ph/file/ba08bd86e253f88a5843e.jpg https://te.legra.ph/file/1ad51d4055399e97ea2b1.jpg https://te.legra.ph/file/2c3ef2cd3f10e25964906.jpg https://te.legra.ph/file/4f3f4ac45bd059e409d2a.jpg https://te.legra.ph/file/ba9a2113cd9a0ff5e4257.jpg https://te.legra.ph/file/d33f369cf7a088ebd2c6b.jpg https://te.legra.ph/file/70917f2f2ec5191fea953.jpg https://te.legra.ph/file/9a52bc8f8f9f4ee4853ed.jpg https://te.legra.ph/file/e8b39ae4daa3f406b7408.jpg https://te.legra.ph/file/57782b16fdaf2afb27703.jpg https://te.legra.ph/file/7ec79cb092fb671bf9ba5.jpg https://te.legra.ph/file/811869dac52a5c69d58eb.jpg https://te.legra.ph/file/fc7f42fa1f16aac3e3559.jpg https://te.legra.ph/file/e8bebc7a3b02d8521a2f3.jpg https://te.legra.ph/file/da488471b4f3ff4cfca72.jpg https://te.legra.ph/file/1a268b817404ca5a0ee5c.jpg https://te.legra.ph/file/a6d5135242c372a12cb6d.jpg https://te.legra.ph/file/4ecf9cd8b86407bdbca75.jpg https://te.legra.ph/file/af67d6071b0c5fafd4721.jpg https://te.legra.ph/file/813a5b738ae52a51776de.jpg https://te.legra.ph/file/b84144dd19ac57fdc8301.jpg https://te.legra.ph/file/03da0b4b19fa5c5cfe4ed.jpg https://te.legra.ph/file/11cab216747f94369ad3d.jpg https://te.legra.ph/file/e375759ce7269989cf323.jpg https://te.legra.ph/file/33be67554e73fc38ddc46.jpg https://te.legra.ph/file/371caa3db3ff14aece791.jpg https://te.legra.ph/file/55683e88e235b6c4961ea.jpg https://te.legra.ph/file/b9ed19297d339e1ee9b4d.jpg https://te.legra.ph/file/aa79948b311ae98eb3e58.jpg https://te.legra.ph/file/fd7a4591e6f6a3486c15a.jpg https://te.legra.ph/file/c6cc2d6331d78b095ffce.jpg https://te.legra.ph/file/cb41f1013fb2ebf8a6915.jpg https://te.legra.ph/file/15dc7bac10656edea2e46.jpg https://te.legra.ph/file/0d9d55996f8aa64e51b41.jpg https://te.legra.ph/file/1b5bb851812dcb6e195b9.jpg https://te.legra.ph/file/8d28842a3253e66385878.jpg https://te.legra.ph/file/122f640cfe640494d1edc.jpg https://te.legra.ph/file/68204ccf443d9968f97df.jpg https://te.legra.ph/file/a3f5c38b81ec6f6331c81.jpg https://te.legra.ph/file/290a0b8b5621cbf6b9421.jpg https://te.legra.ph/file/b0ae4b0c43acaedcd60bc.jpg https://te.legra.ph/file/ff0f68eed17031f092d1e.jpg https://te.legra.ph/file/db7b5b81255755fe2b07a.jpg https://te.legra.ph/file/f0f2ec6333eeaa2066d24.jpg https://te.legra.ph/file/d623821692a6419a7d96d.jpg https://te.legra.ph/file/db2c742f3b16867685e3a.jpg https://te.legra.ph/file/d1bc76930d921a6089a91.jpg https://te.legra.ph/file/bd1636536c80811838cb3.jpg https://te.legra.ph/file/633d5d7a775ad0b8e462c.jpg https://te.legra.ph/file/dc31ed3a2b0b2c7614b0c.jpg https://te.legra.ph/file/39dec9a9fd2f241cd8d3f.jpg https://te.legra.ph/file/ac663b39b2a824729b39f.jpg https://te.legra.ph/file/af84d7c49e330bc66a476.jpg https://te.legra.ph/file/2238a4d0b42feff24650a.jpg https://te.legra.ph/file/8e143b829b6eebb61bf69.jpg https://te.legra.ph/file/319cd42581f27d23a9ce6.jpg https://te.legra.ph/file/a922ef0e55b68707c4730.jpg https://te.legra.ph/file/7ffcadb97ca5018144872.jpg https://te.legra.ph/file/ada33ef4ba0915b378a11.jpg https://te.legra.ph/file/bd85d2361082936fd1145.jpg https://te.legra.ph/file/67c6284d5188a9c0c2b8b.jpg https://te.legra.ph/file/36262342dce2aa77db21a.jpg https://te.legra.ph/file/88da47398ae46ff5f4ba8.jpg https://te.legra.ph/file/4ffb9414510dabccf10d7.jpg https://te.legra.ph/file/39a6adc3cab8a17f17813.jpg https://te.legra.ph/file/084fc46122d642e5c0df3.jpg https://te.legra.ph/file/e37203c709b24f6e128b0.jpg https://te.legra.ph/file/15e91934631e3ebb1be4c.jpg https://te.legra.ph/file/15034a6a4d1195a6e73f7.jpg https://te.legra.ph/file/409ffae08d3764a89eaa4.jpg https://te.legra.ph/file/eadddf137b8abc4e51617.jpg https://te.legra.ph/file/b4ea1636c5b7de3ed52f4.jpg https://te.legra.ph/file/c2e485c62b67e1bfc3fb8.jpg https://te.legra.ph/file/696072272e7401e7e5bf4.jpg https://te.legra.ph/file/8f81b6d3495d0e1125069.jpg https://te.legra.ph/file/97ea65e2e531e654917e2.jpg https://te.legra.ph/file/129779dcf0cb4a8c09259.jpg https://te.legra.ph/file/38527f757731b0c44ad91.jpg https://te.legra.ph/file/55d3d7913e9d8a54e0657.jpg https://te.legra.ph/file/8cc27d1910e74ca3159b1.jpg https://te.legra.ph/file/f35bb674b9ac07c460d3a.jpg https://te.legra.ph/file/d9539862978a379929358.jpg https://te.legra.ph/file/f643fa73138b67effd52c.jpg https://te.legra.ph/file/6c2e0180b95daf7f5085c.jpg https://te.legra.ph/file/4c5282e5599b6ab2d5116.jpg https://te.legra.ph/file/8d01cda092070a8f7ec82.jpg https://te.legra.ph/file/32a1f36669da0b8632a8e.jpg https://te.legra.ph/file/a013ee50360213ef61822.jpg https://te.legra.ph/file/c2dd887db10d8a8f20695.jpg https://te.legra.ph/file/e0458f639e2246b8f172d.jpg https://te.legra.ph/file/e7d939352f74ff9877367.jpg https://te.legra.ph/file/b95fbc6606fc5f037cc37.jpg https://te.legra.ph/file/bcd70e079475c23d4bca9.jpg https://te.legra.ph/file/f11259510a3bd1d8b688f.jpg https://te.legra.ph/file/8d80532a2116c30920901.jpg https://te.legra.ph/file/4fd3bac2b486f7bb19463.jpg https://te.legra.ph/file/2641638c8339e677e719c.jpg https://te.legra.ph/file/03c39092d28fba057c062.jpg https://te.legra.ph/file/8a762a71fc2fceb299207.jpg https://te.legra.ph/file/e6e2f3ec3e8b31588a097.jpg https://te.legra.ph/file/c4e1f77e7bc9ab86d8b47.jpg https://te.legra.ph/file/6c38bd86474ef584434bc.jpg https://te.legra.ph/file/815417ff0aea757b18f4e.jpg https://te.legra.ph/file/19ff890677c0fa6b587cf.jpg https://te.legra.ph/file/124f00dcfddd0218e48c4.jpg https://te.legra.ph/file/ee624ab1850e914bac6dc.jpg https://te.legra.ph/file/3aad3c44e13670ed0e50e.jpg https://te.legra.ph/file/d0059bad1846a97498b88.jpg https://te.legra.ph/file/acaf6c643451960061b15.jpg https://te.legra.ph/file/2a35ea7f236704556255c.jpg https://te.legra.ph/file/9b028a521676e79abd066.jpg https://te.legra.ph/file/b4587c390ef12abceb82b.jpg https://te.legra.ph/file/4f3baaa279f7f18346893.jpg https://te.legra.ph/file/5f5eb039b910005e4230c.jpg https://te.legra.ph/file/16ae1d4d5ff0c9ec32790.jpg https://te.legra.ph/file/fcb129fb067f54fed4a60.jpg https://te.legra.ph/file/eb2dd2eaef1480d4ded50.jpg https://te.legra.ph/file/fbec3c95b3b39b7d3a4d5.jpg https://te.legra.ph/file/d1424b3579ff41d4ec451.jpg https://te.legra.ph/file/12b6e432fb0ff578d490c.jpg https://te.legra.ph/file/52d96b675e15b258cefd6.jpg https://te.legra.ph/file/5ee2ebbfdf2c6eb533b77.jpg https://te.legra.ph/file/c35a67d6c523bff24c46e.jpg https://te.legra.ph/file/5c1d56f37e2b530ccd465.jpg https://te.legra.ph/file/4eddaedca9424475fe766.jpg https://te.legra.ph/file/d813b73b9696e25931913.jpg https://te.legra.ph/file/5bdcec9b8587ba84fe6b4.jpg https://te.legra.ph/file/c6a4d67e8c9280e255a1d.jpg https://te.legra.ph/file/dd9bb2ce1fd09116ee7b2.jpg https://te.legra.ph/file/fb467bbf55f528a350bdf.jpg https://te.legra.ph/file/1e9c51278d84348b2a991.jpg https://te.legra.ph/file/04302861a3bc7db64bc5b.jpg https://te.legra.ph/file/898f5e44d05f2b870bde5.jpg https://te.legra.ph/file/9396ab1a7b370203832cc.jpg https://te.legra.ph/file/6c0ca2fc70673dd1b43ab.jpg https://te.legra.ph/file/27afda645eab8b3c3032b.jpg https://te.legra.ph/file/d66d3ec4fa5936eb9bc36.jpg https://te.legra.ph/file/7ae3a8e6ced5cb2116e3f.jpg https://te.legra.ph/file/bac42320a5aab0789b2e1.jpg https://te.legra.ph/file/fdf420d076c01417bb145.jpg https://te.legra.ph/file/edccb1eefb48330450e13.jpg https://te.legra.ph/file/ceca24c11bcdae08348ce.jpg https://te.legra.ph/file/875f01d54d605029a9efc.jpg https://te.legra.ph/file/a87933036982008b78a31.jpg https://te.legra.ph/file/ee472d718a46b609addd2.jpg https://te.legra.ph/file/40d9e3ef88e65560a3ab1.jpg https://te.legra.ph/file/3f9f9116452d3e1edb436.jpg https://te.legra.ph/file/757e073157dd95f85e738.jpg https://te.legra.ph/file/fd1e15d83c392db10a3f2.jpg https://te.legra.ph/file/720eb915ba347ae009582.jpg https://te.legra.ph/file/975881e1b59af098ad77b.jpg https://te.legra.ph/file/1e65bf45a93d86a183b73.jpg https://te.legra.ph/file/3dc9dc291c08018bae011.jpg https://te.legra.ph/file/39593a1f3933c24291bbc.jpg https://te.legra.ph/file/6df5060ec4f0d9f1f44d7.jpg https://te.legra.ph/file/d0349c7055880200ffafd.jpg https://te.legra.ph/file/76d5230815d2405c1668a.jpg https://te.legra.ph/file/3d6e09d4fb40530306f41.jpg https://te.legra.ph/file/51ed1cb61043f6c1e8537.jpg https://te.legra.ph/file/c59fa9ed1d14746074447.jpg https://te.legra.ph/file/db18cc41231f02041770d.jpg https://te.legra.ph/file/61418378bea7b0441322d.jpg https://te.legra.ph/file/0d97d6d600cd093277d80.jpg https://te.legra.ph/file/797490f2bfbfabf555618.jpg https://te.legra.ph/file/c00322b87c357045a879a.jpg https://te.legra.ph/file/83e28af7bb1e209846f9f.jpg https://te.legra.ph/file/8a29b18d82494d3aa72de.jpg https://te.legra.ph/file/5668ea90426f880e662f2.jpg https://te.legra.ph/file/efc7e058417efc0973363.jpg https://te.legra.ph/file/8707110878fea654f46a9.jpg https://te.legra.ph/file/d41f9093c21b87e8383a4.jpg https://te.legra.ph/file/dd5ea167992a1b084c171.jpg https://te.legra.ph/file/229df32e6a4a2505940fb.jpg https://te.legra.ph/file/b105435a02e44aa7dc496.jpg https://te.legra.ph/file/7216e66cc5c8f7cc18393.jpg https://te.legra.ph/file/fa696ed0f51ee529c042f.jpg https://te.legra.ph/file/ceef268e2b4dbc58d8ad9.jpg https://te.legra.ph/file/252dd96d308f10286a411.jpg https://te.legra.ph/file/4ba0bc7021d8f558c0bab.jpg https://te.legra.ph/file/9efb6d5cd5da0c5626dc5.jpg https://te.legra.ph/file/842508e53596b5b3ac840.jpg https://te.legra.ph/file/b3b2637561e5a567a4963.jpg https://te.legra.ph/file/c8169a82ba25ec0de1945.jpg https://te.legra.ph/file/c2685fbaa71f3479cab5a.jpg https://te.legra.ph/file/da3de06d612efef216a98.jpg https://te.legra.ph/file/2754c5a59e7f9b9293274.jpg https://te.legra.ph/file/5b197bf08ef36432bbc4a.jpg https://te.legra.ph/file/6484ba5952fd28f8aaca9.jpg https://te.legra.ph/file/f2bec8abef087dc981fd7.jpg https://te.legra.ph/file/efb4700bd4172609283ab.jpg https://te.legra.ph/file/339f418f6c4cddfb2aec0.jpg https://te.legra.ph/file/e17eda4e8cf2da708b88b.jpg https://te.legra.ph/file/fc1fde08124c2378bb581.jpg https://te.legra.ph/file/c357fc8d253603facd459.jpg https://te.legra.ph/file/719254fb911955514cd79.jpg https://te.legra.ph/file/a1d0accd962bf690e90f3.jpg https://te.legra.ph/file/b947a30ff5964ab57b18f.jpg https://te.legra.ph/file/0b5da11644e6bd74104cb.jpg https://te.legra.ph/file/a3ea5c36761666612f457.jpg https://te.legra.ph/file/ee6726a4ed083f2baac3c.jpg https://te.legra.ph/file/48b2c0d642281c3712d6d.jpg https://te.legra.ph/file/59fe460ce2810d8bce926.jpg https://te.legra.ph/file/cae19d5b4f08b99336852.jpg https://te.legra.ph/file/923928ee192a62eac3808.jpg https://te.legra.ph/file/b73b98c9ea8cce6528129.jpg https://te.legra.ph/file/d6db2d45a97269f417f7f.jpg https://te.legra.ph/file/b838fb17a7acbd3907c26.jpg https://te.legra.ph/file/701dcf63b05e8c6d79376.jpg https://te.legra.ph/file/11ccbd7b8c9122b76048d.jpg https://te.legra.ph/file/6d86eef258d8e805702b0.jpg https://te.legra.ph/file/d2a3e7d5bbdaf90a033fd.jpg https://te.legra.ph/file/b0de0532ee3c32527538c.jpg https://te.legra.ph/file/f2bee4154c59a4a03c409.jpg https://te.legra.ph/file/387602441c648c23c1cc1.jpg https://te.legra.ph/file/72310f36098ab8ee66060.jpg https://te.legra.ph/file/0973e77c2396b5f9e7d50.jpg https://te.legra.ph/file/cbe5aeff409402e574b8a.jpg https://te.legra.ph/file/2d45c3b75b179b13f7e2c.jpg https://te.legra.ph/file/78baca983fa2738bbd815.jpg https://te.legra.ph/file/11fc111a19052e4cd0722.jpg https://te.legra.ph/file/605413277064806580602.jpg https://te.legra.ph/file/60cd43418ef54d900ec8a.jpg https://te.legra.ph/file/c9aa2fc41d1dc8b6387c4.jpg https://te.legra.ph/file/ec18a08f908b905454fb0.jpg https://te.legra.ph/file/a844b030e0c92f8cfc00d.jpg https://te.legra.ph/file/f49cacfa07082bbd71f95.jpg https://te.legra.ph/file/78882e28aca4e26a5f3a5.jpg https://te.legra.ph/file/72cbadb922dc159f2d701.jpg https://te.legra.ph/file/910a1783e6f9c226bc188.jpg https://te.legra.ph/file/55dafaf7599082d443d7b.jpg https://te.legra.ph/file/ee282fc90de6768891d46.jpg https://te.legra.ph/file/0e413518e4641db4d1764.jpg https://te.legra.ph/file/f19ba1d8b6f29b72467a5.jpg https://te.legra.ph/file/9e4e4c044092bf1c2dc00.jpg https://te.legra.ph/file/77ca7730e093e0f5c2f1b.jpg https://te.legra.ph/file/88cdb9a047d8e1b3e2dfd.jpg https://te.legra.ph/file/e83d07fb78670aad434b3.jpg https://te.legra.ph/file/d3f2dfb60c669e0bb9e1c.jpg https://te.legra.ph/file/74e1cca0a17cb5e8a72f1.jpg https://te.legra.ph/file/8996a7363c3106ae97bc7.jpg https://te.legra.ph/file/b6936c72148eceb93658a.jpg https://te.legra.ph/file/8bfd933ce5bdc4c446c64.jpg https://te.legra.ph/file/e95c7e7c891495fb86803.jpg https://te.legra.ph/file/eab77598990043bd3e43a.jpg https://te.legra.ph/file/05f88effc97b84265e7a9.jpg https://te.legra.ph/file/1d4065f3455be5d247b91.jpg https://te.legra.ph/file/dd1bb21f23a0761655260.jpg https://te.legra.ph/file/0050f28cb73092adadb48.jpg https://te.legra.ph/file/b375d5c44c25ce0b94541.jpg https://te.legra.ph/file/9848b75185d004ad5aab5.jpg https://te.legra.ph/file/c3ab631f327fa92316cae.jpg https://te.legra.ph/file/d08c675528ad6ff726d84.jpg https://te.legra.ph/file/a523d6e197476a300f45f.jpg https://te.legra.ph/file/c2ad82074f7e6b302a3e9.jpg https://te.legra.ph/file/0435b78fb2d2a44554fb3.jpg https://te.legra.ph/file/514e0e0595ae46662ae1d.jpg https://te.legra.ph/file/ac8dc3d1b01ea6237184d.jpg https://te.legra.ph/file/72d37c0aae9ae8b3edc42.jpg https://te.legra.ph/file/39c5980b84ef7e37f7f07.jpg https://te.legra.ph/file/4e55874181ef6cfbd9633.jpg https://te.legra.ph/file/26d02c4f59ad9e2016b88.jpg https://te.legra.ph/file/8671b899452634d356646.jpg https://te.legra.ph/file/d2b988cf218306998a73f.jpg https://te.legra.ph/file/2228f9efe9b2b12547978.jpg https://te.legra.ph/file/a376636b5904f27837a22.jpg https://te.legra.ph/file/cbf3cf51d1fc4381df424.jpg https://te.legra.ph/file/fa09645267bdf80e9383b.jpg https://te.legra.ph/file/9c30e8f1e24b67fa295d1.jpg https://te.legra.ph/file/cbe83c8cc679b703ec1c8.jpg https://te.legra.ph/file/ad9b28b53ab4128b1c26f.jpg https://te.legra.ph/file/d33b4a66f3b54ad288239.jpg https://te.legra.ph/file/a235857e82174f3ef9f91.jpg https://te.legra.ph/file/ccda48800fb133d80439e.jpg https://te.legra.ph/file/6bad2aeff8ceb2b56aaea.jpg https://te.legra.ph/file/bf797b1d5e3ac78c6243a.jpg https://te.legra.ph/file/6b5a18f6bd35c85b9e732.jpg https://te.legra.ph/file/c6f47d0f7d9b64600c6cf.jpg https://te.legra.ph/file/af9e3cd494f60bb7d8c74.jpg https://te.legra.ph/file/6a7cc00a6041ef055b39b.jpg https://te.legra.ph/file/95df54af077da4491e1ab.jpg https://te.legra.ph/file/fc4dbe2dd4ca437daad3c.jpg https://te.legra.ph/file/784c03a5cf5fae6667973.jpg https://te.legra.ph/file/bb2a2f5c6167dc6adf221.jpg https://te.legra.ph/file/2a491ec61d42c576b5c9d.jpg https://te.legra.ph/file/f572b3e3ba4ff4243515f.jpg https://te.legra.ph/file/b60202a0464f47ccfd065.jpg https://te.legra.ph/file/983f29b4ceeeeb9411b36.jpg https://te.legra.ph/file/23b3da4d838322266aa15.jpg https://te.legra.ph/file/cafc4e4e6f53647b6404a.jpg https://te.legra.ph/file/5fb6a32f9ce8c2592b2ff.jpg https://te.legra.ph/file/c5023e22667d0ab25a189.jpg https://te.legra.ph/file/f7f06ba9400477fb9a5e3.jpg https://te.legra.ph/file/cc4f65e337b8bcd0dc81f.jpg https://te.legra.ph/file/18c56b4d317e96e9349dc.jpg https://te.legra.ph/file/dcea81eb162f3247ae97c.jpg https://te.legra.ph/file/222991437631fd71810eb.jpg https://te.legra.ph/file/3ac2b5de5aecc1b6ff0b0.jpg https://te.legra.ph/file/b3dbd28fac65d41149212.jpg https://te.legra.ph/file/2beed36863054e1b71375.jpg https://te.legra.ph/file/8c5197254c58000811133.jpg https://te.legra.ph/file/5361493695006d1afbefc.jpg https://te.legra.ph/file/4f7e8478fb362a4423d34.jpg https://te.legra.ph/file/49be698ad337859a51b37.jpg https://te.legra.ph/file/a55a7199e6268f5e183be.jpg https://te.legra.ph/file/43aa92b28df3a802cf99b.jpg https://te.legra.ph/file/a7153540572b8e861cdad.jpg https://te.legra.ph/file/a640d508d75369e5d23c4.jpg https://te.legra.ph/file/9820d310a5a4068efede8.jpg https://te.legra.ph/file/0fce92dc92d584b04d0d5.jpg https://te.legra.ph/file/a6c189f630c957b10ae68.jpg https://te.legra.ph/file/d24d6fc985f85db68b855.jpg https://te.legra.ph/file/edb754b1714089b9c6c8a.jpg https://te.legra.ph/file/50a7d447f4d5a53c391c0.jpg https://te.legra.ph/file/62e2fdcccd7aa7609e73e.jpg https://te.legra.ph/file/bb5cf67561434769039c0.jpg https://te.legra.ph/file/68762a9dedfdeddb6cd70.jpg https://te.legra.ph/file/e2d9de3e3c71a88630960.jpg https://te.legra.ph/file/d17bc26a9338566fc1fea.jpg https://te.legra.ph/file/25831a0b68046486a6b75.jpg https://te.legra.ph/file/20236ccfc2db17545113c.jpg https://te.legra.ph/file/dde6f4c998bbcdfad115b.jpg https://te.legra.ph/file/a34f86c84b3716ddf95fa.jpg https://te.legra.ph/file/f27dfa43717044d497161.jpg https://te.legra.ph/file/c29bb864b3a0e8babea7f.jpg https://te.legra.ph/file/7070a91cb92597a713bb6.jpg https://te.legra.ph/file/cb89ac05474c1ebb423ef.jpg https://te.legra.ph/file/147ab583574f35a900649.jpg https://te.legra.ph/file/67cd182d137f7c865b621.jpg https://te.legra.ph/file/63ee67005a751d01a64b3.jpg https://te.legra.ph/file/657e0cf4cce577663e483.jpg https://te.legra.ph/file/3f881189dfb058c809c92.jpg https://te.legra.ph/file/e0d3f70217423e3383149.jpg https://te.legra.ph/file/03f9bb09660437ed00bb1.jpg https://te.legra.ph/file/8175c55fe13ac47472cf9.jpg https://te.legra.ph/file/cefdac79199e8026b291e.jpg https://te.legra.ph/file/b0d866d09ae105fa874a8.jpg https://te.legra.ph/file/fbaaf361575dc9288f013.jpg https://te.legra.ph/file/479bbadb86d1c1dfb8f4d.jpg',
                  'RSS_DELAY': 900,
                  'DEF_ANI_TEMP': '''<b>{ro_title}</b>({na_title})
                                     <b>Format</b>: <code>{format}</code>
                                     <b>Status</b>: <code>{status}</code>
                                     <b>Start Date</b>: <code>{startdate}</code>
                                     <b>End Date</b>: <code>{enddate}</code>
                                     <b>Season</b>: <code>{season}</code>
                                     <b>Country</b>: {country}
                                     <b>Episodes</b>: <code>{episodes}</code>
                                     <b>Duration</b>: <code>{duration}</code>
                                     <b>Average Score</b>: <code>{avgscore}</code>
                                     <b>Genres</b>: {genres}
                                     <b>Hashtag</b>: {hashtag}
                                     <b>Studios</b>: {studios}

                                     <b>Description</b>: <i>{description}</i>''',
                  'DEF_IMDB_TEMP': '''<b>Title: </b> {title} [{year}]
                                      <b>Also Known As:</b> {aka}
                                      <b>Rating ⭐️:</b> <i>{rating}</i>
                                      <b>Release Info: </b> <a href="{url_releaseinfo}">{release_date}</a>
                                      <b>Genre: </b>{genres}
                                      <b>IMDb URL:</b> {url}
                                      <b>Language: </b>{languages}
                                      <b>Country of Origin : </b> {countries}
                                      
                                      <b>Story Line: </b><code>{plot}</code>
                                      
                                      <a href="{url_cast}">Read More ...</a>'''}



def load_config():

    BOT_TOKEN = environ.get('BOT_TOKEN', '')
    if len(BOT_TOKEN) == 0:
        BOT_TOKEN = config_dict['BOT_TOKEN']

    TELEGRAM_API = environ.get('TELEGRAM_API', '')
    if len(TELEGRAM_API) == 0:
        TELEGRAM_API = config_dict['TELEGRAM_API']
    else:
        TELEGRAM_API = int(TELEGRAM_API)

    TELEGRAM_HASH = environ.get('TELEGRAM_HASH', '')
    if len(TELEGRAM_HASH) == 0:
        TELEGRAM_HASH = config_dict['TELEGRAM_HASH']

    OWNER_ID = environ.get('OWNER_ID', '')
    if len(OWNER_ID) == 0:
        OWNER_ID = config_dict['OWNER_ID']
    else:
        OWNER_ID = int(OWNER_ID)

    DATABASE_URL = environ.get('DATABASE_URL', '')
    if len(DATABASE_URL) == 0:
        DATABASE_URL = ''

    DOWNLOAD_DIR = environ.get('DOWNLOAD_DIR', '')
    if len(DOWNLOAD_DIR) == 0:
        DOWNLOAD_DIR = '/usr/src/app/downloads/'
    elif not DOWNLOAD_DIR.endswith("/"):
        DOWNLOAD_DIR = f'{DOWNLOAD_DIR}/'


    GDRIVE_ID = environ.get('GDRIVE_ID', '')
    if len(GDRIVE_ID) == 0:
        GDRIVE_ID = ''

    TGH_THUMB = environ.get('TGH_THUMB', '')
    if len(TGH_THUMB) == 0:
        TGH_THUMB = 'https://te.legra.ph/file/3325f4053e8d68eab07b5.jpg'

    AUTHORIZED_CHATS = environ.get('AUTHORIZED_CHATS', '')
    if len(AUTHORIZED_CHATS) != 0:
        aid = AUTHORIZED_CHATS.split()
        for id_ in aid:
            user_data[int(id_.strip())] = {'is_auth': True}

    SUDO_USERS = environ.get('SUDO_USERS', '')
    if len(SUDO_USERS) != 0:
        aid = SUDO_USERS.split()
        for id_ in aid:
            user_data[int(id_.strip())] = {'is_sudo': True}

    PAID_USERS = environ.get('PAID_USERS', '')
    if len(PAID_USERS) != 0:    
        aid = PAID_USERS.split()
        for id_ in aid:
            user_data[int(id_.strip())] = {'is_paid': True}

    LOG_LEECH = environ.get('LOG_LEECH', '')
    if len(LOG_LEECH) != 0: 
        aid = LOG_LEECH.split(' ')
        user_data['is_log_leech'] = [int(id_.strip()) for id_ in aid]

    LEECH_LOG = environ.get('LEECH_LOG', '')
    if len(LEECH_LOG) != 0: 
        aid = LEECH_LOG.split(' ')
        user_data['is_leech_log'] = [int(id_.strip()) for id_ in aid]

    MIRROR_LOGS = environ.get('MIRROR_LOGS', '')
    if len(MIRROR_LOGS) != 0:   
        aid = MIRROR_LOGS.split(' ')
        user_data['mirror_logs'] = [int(id_.strip()) for id_ in aid]

    LINK_LOGS = environ.get('LINK_LOGS', '')
    if len(LINK_LOGS) != 0: 
        aid = LINK_LOGS.split(' ')
        user_data['link_logs'] = [int(id_.strip()) for id_ in aid]

    EXTENSION_FILTER = environ.get('EXTENSION_FILTER', '')
    if len(EXTENSION_FILTER) > 0:
        fx = EXTENSION_FILTER.split()
        GLOBAL_EXTENSION_FILTER.clear()
        GLOBAL_EXTENSION_FILTER.append('.aria2')
        for x in fx:
            GLOBAL_EXTENSION_FILTER.append(x.strip().lower())

    tgBotMaxFileSize = 2097151000

    TG_SPLIT_SIZE = environ.get('TG_SPLIT_SIZE', '')
    if len(TG_SPLIT_SIZE) == 0 or int(TG_SPLIT_SIZE) > tgBotMaxFileSize:
        TG_SPLIT_SIZE = tgBotMaxFileSize
    else:
        TG_SPLIT_SIZE = int(TG_SPLIT_SIZE)

    MEGA_API_KEY = environ.get('MEGA_API_KEY', '')
    if len(MEGA_API_KEY) == 0:
        MEGA_API_KEY = ''

    MEGA_EMAIL_ID = environ.get('MEGA_EMAIL_ID', '')
    MEGA_PASSWORD = environ.get('MEGA_PASSWORD', '')
    if len(MEGA_EMAIL_ID) == 0 or len(MEGA_PASSWORD) == 0:
        MEGA_EMAIL_ID = ''
        MEGA_PASSWORD = ''

    STATUS_LIMIT = environ.get('STATUS_LIMIT', '')
    STATUS_LIMIT = '' if len(STATUS_LIMIT) == 0 else int(STATUS_LIMIT)

    UPTOBOX_TOKEN = environ.get('UPTOBOX_TOKEN', '')
    if len(UPTOBOX_TOKEN) == 0:
        UPTOBOX_TOKEN = ''

    INDEX_URL = environ.get('INDEX_URL', '').rstrip("/")
    if len(INDEX_URL) == 0:
        INDEX_URL = ''

    SEARCH_API_LINK = environ.get('SEARCH_API_LINK', '').rstrip("/")
    if len(SEARCH_API_LINK) == 0:
        SEARCH_API_LINK = ''

    STATUS_UPDATE_INTERVAL = environ.get('STATUS_UPDATE_INTERVAL', '')
    if len(STATUS_UPDATE_INTERVAL) == 0:
        STATUS_UPDATE_INTERVAL = 10
    else:
        STATUS_UPDATE_INTERVAL = int(STATUS_UPDATE_INTERVAL)
    if len(download_dict) != 0:
        with status_reply_dict_lock:
            if Interval:
                Interval[0].cancel()
                Interval.clear()
                Interval.append(setInterval(STATUS_UPDATE_INTERVAL, update_all_messages))

    AUTO_DELETE_MESSAGE_DURATION = environ.get('AUTO_DELETE_MESSAGE_DURATION', '')
    if len(AUTO_DELETE_MESSAGE_DURATION) == 0:
        AUTO_DELETE_MESSAGE_DURATION = 30
    else:
        AUTO_DELETE_MESSAGE_DURATION = int(AUTO_DELETE_MESSAGE_DURATION)

    AUTO_DELETE_UPLOAD_MESSAGE_DURATION = environ.get('AUTO_DELETE_UPLOAD_MESSAGE_DURATION', '')
    if len(AUTO_DELETE_UPLOAD_MESSAGE_DURATION) == 0:   
        AUTO_DELETE_UPLOAD_MESSAGE_DURATION = -1
    else:   
        AUTO_DELETE_UPLOAD_MESSAGE_DURATION = int(AUTO_DELETE_UPLOAD_MESSAGE_DURATION)

    SEARCH_LIMIT = environ.get('SEARCH_LIMIT', '')
    SEARCH_LIMIT = 0 if len(SEARCH_LIMIT) == 0 else int(SEARCH_LIMIT)

    CMD_PERFIX = environ.get('CMD_PERFIX', '')

    USER_SESSION_STRING = environ.get('USER_SESSION_STRING', '')

    TORRENT_TIMEOUT = environ.get('TORRENT_TIMEOUT', '')
    downloads = aria2.get_downloads()
    if len(TORRENT_TIMEOUT) == 0:
        if downloads:
            aria2.set_options({'bt-stop-timeout': '0'}, downloads)
        aria2_options['bt-stop-timeout'] = '0'
    else:
        if downloads:
            aria2.set_options({'bt-stop-timeout': TORRENT_TIMEOUT}, downloads)
        aria2_options['bt-stop-timeout'] = TORRENT_TIMEOUT
        TORRENT_TIMEOUT = int(TORRENT_TIMEOUT)


    TORRENT_DIRECT_LIMIT = environ.get('TORRENT_DIRECT_LIMIT', '')
    TORRENT_DIRECT_LIMIT = '' if len(TORRENT_DIRECT_LIMIT) == 0 else float(TORRENT_DIRECT_LIMIT)

    CLONE_LIMIT = environ.get('CLONE_LIMIT', '')
    CLONE_LIMIT = '' if len(CLONE_LIMIT) == 0 else float(CLONE_LIMIT)

    LEECH_LIMIT = environ.get('LEECH_LIMIT', '')
    LEECH_LIMIT = '' if len(LEECH_LIMIT) == 0 else float(LEECH_LIMIT)

    MEGA_LIMIT = environ.get('MEGA_LIMIT', '')
    MEGA_LIMIT = '' if len(MEGA_LIMIT) == 0 else float(MEGA_LIMIT)

    STORAGE_THRESHOLD = environ.get('STORAGE_THRESHOLD', '')
    STORAGE_THRESHOLD = '' if len(STORAGE_THRESHOLD) == 0 else float(STORAGE_THRESHOLD)

    ZIP_UNZIP_LIMIT = environ.get('ZIP_UNZIP_LIMIT', '')
    ZIP_UNZIP_LIMIT = '' if len(ZIP_UNZIP_LIMIT) == 0 else float(ZIP_UNZIP_LIMIT)

    TOTAL_TASKS_LIMIT = environ.get('TOTAL_TASKS_LIMIT', '')
    TOTAL_TASKS_LIMIT = '' if len(TOTAL_TASKS_LIMIT) == 0 else int(TOTAL_TASKS_LIMIT)

    USER_TASKS_LIMIT = environ.get('USER_TASKS_LIMIT', '')
    USER_TASKS_LIMIT = '' if len(USER_TASKS_LIMIT) == 0 else int(USER_TASKS_LIMIT)


    INCOMPLETE_TASK_NOTIFIER = environ.get('INCOMPLETE_TASK_NOTIFIER', '')
    INCOMPLETE_TASK_NOTIFIER = INCOMPLETE_TASK_NOTIFIER.lower() == 'true'
    if not INCOMPLETE_TASK_NOTIFIER and DATABASE_URL:
        DbManger().trunc_table('tasks')


    STOP_DUPLICATE = environ.get('STOP_DUPLICATE', '')
    STOP_DUPLICATE = STOP_DUPLICATE.lower() == 'true'

    VIEW_LINK = environ.get('VIEW_LINK', '')
    VIEW_LINK = VIEW_LINK.lower() == 'true'

    SET_BOT_COMMANDS = environ.get('SET_BOT_COMMANDS', '')
    SET_BOT_COMMANDS = SET_BOT_COMMANDS.lower() == 'true'

    IS_TEAM_DRIVE = environ.get('IS_TEAM_DRIVE', '')
    IS_TEAM_DRIVE = IS_TEAM_DRIVE.lower() == 'true'

    USE_SERVICE_ACCOUNTS = environ.get('USE_SERVICE_ACCOUNTS', '')
    USE_SERVICE_ACCOUNTS = USE_SERVICE_ACCOUNTS.lower() == 'true'

    WEB_PINCODE = environ.get('WEB_PINCODE', '')
    WEB_PINCODE = WEB_PINCODE.lower() == 'true'

    AS_DOCUMENT = environ.get('AS_DOCUMENT', '')
    AS_DOCUMENT = AS_DOCUMENT.lower() == 'true'

    EQUAL_SPLITS = environ.get('EQUAL_SPLITS', '')
    EQUAL_SPLITS = EQUAL_SPLITS.lower() == 'true'

    IGNORE_PENDING_REQUESTS = environ.get('IGNORE_PENDING_REQUESTS', '')
    IGNORE_PENDING_REQUESTS = IGNORE_PENDING_REQUESTS.lower() == 'true'

    RSS_CHAT_ID = environ.get('RSS_CHAT_ID', '')
    RSS_CHAT_ID = '' if len(RSS_CHAT_ID) == 0 else int(RSS_CHAT_ID)

    RSS_DELAY = environ.get('RSS_DELAY', '')
    RSS_DELAY = 900 if len(RSS_DELAY) == 0 else int(RSS_DELAY)

    RSS_COMMAND = environ.get('RSS_COMMAND', '')
    if len(RSS_COMMAND) == 0:
        RSS_COMMAND = ''

    SERVER_PORT = environ.get('SERVER_PORT', '')
    SERVER_PORT = 80 if len(SERVER_PORT) == 0 else int(SERVER_PORT)

    DRIVES_IDS.clear()
    DRIVES_NAMES.clear()
    INDEX_URLS.clear()

    if GDRIVE_ID:
        DRIVES_NAMES.append("Main")
        DRIVES_IDS.append(GDRIVE_ID)
        INDEX_URLS.append(INDEX_URL)

    if ospath.exists('list_drives.txt'):
        with open('list_drives.txt', 'r+') as f:
            lines = f.readlines()
            for line in lines:
                temp = line.strip().split()
                DRIVES_IDS.append(temp[1])
                DRIVES_NAMES.append(temp[0].replace("_", " "))
                if len(temp) > 2:
                    INDEX_URLS.append(temp[2])
                else:
                    INDEX_URLS.append('')

    SEARCH_PLUGINS = environ.get('SEARCH_PLUGINS', '')
    if len(SEARCH_PLUGINS) == 0:
        SEARCH_PLUGINS = ''

    UPSTREAM_REPO = environ.get('UPSTREAM_REPO', '')
    if len(UPSTREAM_REPO) == 0: 
        UPSTREAM_REPO = 'https://github.com/weebzone/WZML'

    UPSTREAM_BRANCH = environ.get('UPSTREAM_BRANCH', '')
    if len(UPSTREAM_BRANCH) == 0:   
        UPSTREAM_BRANCH = 'master'

    UPDATE_PACKAGES = environ.get('UPDATE_PACKAGES', '')
    if len(UPDATE_PACKAGES) == 0:
        UPDATE_PACKAGES = 'False'

    MIRROR_ENABLED = environ.get('MIRROR_ENABLED', '')
    MIRROR_ENABLED = MIRROR_ENABLED.lower() == 'true'

    LEECH_ENABLED = environ.get('LEECH_ENABLED', '')
    LEECH_ENABLED = LEECH_ENABLED.lower() == 'true'

    WATCH_ENABLED = environ.get('WATCH_ENABLED', '')
    WATCH_ENABLED = WATCH_ENABLED.lower() == 'true'

    CLONE_ENABLED = environ.get('CLONE_ENABLED', '')
    CLONE_ENABLED = CLONE_ENABLED.lower() == 'true'

    ANILIST_ENABLED = environ.get('ANILIST_ENABLED', '')
    ANILIST_ENABLED = ANILIST_ENABLED.lower() == 'true'

    WAYBACK_ENABLED = environ.get('WAYBACK_ENABLED', '')
    WAYBACK_ENABLED = WAYBACK_ENABLED.lower() == 'true'

    MEDIAINFO_ENABLED = environ.get('MEDIAINFO_ENABLED', '')
    MEDIAINFO_ENABLED = MEDIAINFO_ENABLED.lower() == 'true'

    TELEGRAPH_STYLE = environ.get('TELEGRAPH_STYLE', '')
    TELEGRAPH_STYLE = TELEGRAPH_STYLE.lower() == 'true'

    EMOJI_THEME = environ.get('EMOJI_THEME', '')
    EMOJI_THEME = EMOJI_THEME.lower() == 'true'

    DISABLE_DRIVE_LINK = environ.get('DISABLE_DRIVE_LINK', '')
    DISABLE_DRIVE_LINK = DISABLE_DRIVE_LINK.lower() == 'true'

    LEECH_LOG_INDEXING = environ.get('LEECH_LOG_INDEXING', '')
    LEECH_LOG_INDEXING = LEECH_LOG_INDEXING.lower() == 'true'

    BOT_PM = environ.get('BOT_PM', '')
    BOT_PM = BOT_PM.lower() == 'true'

    FORCE_BOT_PM = environ.get('FORCE_BOT_PM', '')
    FORCE_BOT_PM = FORCE_BOT_PM.lower() == 'true'

    SOURCE_LINK = environ.get('SOURCE_LINK', '')
    SOURCE_LINK = SOURCE_LINK.lower() == 'true'

    FSUB = environ.get('FSUB', '')
    FSUB = FSUB.lower() == 'true'

    PAID_SERVICE = environ.get('PAID_SERVICE', '')
    PAID_SERVICE = PAID_SERVICE.lower() == 'true'

    SHOW_LIMITS_IN_STATS = environ.get('SHOW_LIMITS_IN_STATS', '')
    SHOW_LIMITS_IN_STATS = SHOW_LIMITS_IN_STATS.lower() == 'true'

    START_BTN1_NAME = environ.get('START_BTN1_NAME', '')
    START_BTN1_URL = environ.get('START_BTN1_URL', '')
    if len(START_BTN1_NAME) == 0 or len(START_BTN1_URL) == 0:   
        START_BTN1_NAME = 'Master'
        START_BTN1_URL = 'https://t.me/krn_adhikari'

    START_BTN2_NAME = environ.get('START_BTN2_NAME', '')
    START_BTN2_URL = environ.get('START_BTN2_URL', '')
    if len(START_BTN2_NAME) == 0 or len(START_BTN2_URL) == 0:   
        START_BTN2_NAME = 'Support Group'
        START_BTN2_URL = 'https://t.me/WeebZone_updates'

    BUTTON_FOUR_NAME = environ.get('BUTTON_FOUR_NAME', '')
    BUTTON_FOUR_URL = environ.get('BUTTON_FOUR_URL', '')
    if len(BUTTON_FOUR_NAME) == 0 or len(BUTTON_FOUR_URL) == 0: 
        BUTTON_FOUR_NAME = ''
        BUTTON_FOUR_URL = ''

    BUTTON_FIVE_NAME = environ.get('BUTTON_FIVE_NAME', '')
    BUTTON_FIVE_URL = environ.get('BUTTON_FIVE_URL', '')
    if len(BUTTON_FIVE_NAME) == 0 or len(BUTTON_FIVE_URL) == 0: 
        BUTTON_FIVE_NAME = ''
        BUTTON_FIVE_URL = ''

    BUTTON_SIX_NAME = environ.get('BUTTON_SIX_NAME', '')
    BUTTON_SIX_URL = environ.get('BUTTON_SIX_URL', '')
    if len(BUTTON_SIX_NAME) == 0 or len(BUTTON_SIX_URL) == 0:   
        BUTTON_SIX_NAME = ''
        BUTTON_SIX_URL = ''

    SHORTENER = environ.get('SHORTENER', '')
    SHORTENER_API = environ.get('SHORTENER_API', '')
    if len(SHORTENER) == 0 or len(SHORTENER_API) == 0:  
        SHORTENER = ''
        SHORTENER_API = ''

    UNIFIED_EMAIL = environ.get('UNIFIED_EMAIL', '')
    if len(UNIFIED_EMAIL) == 0:
        UNIFIED_EMAIL = ''

    UNIFIED_PASS = environ.get('UNIFIED_PASS', '')
    if len(UNIFIED_PASS) == 0:
        UNIFIED_PASS = ''

    GDTOT_CRYPT = environ.get('GDTOT_CRYPT', '')
    if len(GDTOT_CRYPT) == 0:
        GDTOT_CRYPT = ''

    HUBDRIVE_CRYPT = environ.get('HUBDRIVE_CRYPT', '')
    if len(HUBDRIVE_CRYPT) == 0:
        HUBDRIVE_CRYPT = ''

    KATDRIVE_CRYPT = environ.get('KATDRIVE_CRYPT', '')
    if len(KATDRIVE_CRYPT) == 0:
        KATDRIVE_CRYPT = ''

    DRIVEFIRE_CRYPT = environ.get('DRIVEFIRE_CRYPT', '')
    if len(DRIVEFIRE_CRYPT) == 0:
        DRIVEFIRE_CRYPT = ''

    SHAREDRIVE_PHPCKS = environ.get('SHAREDRIVE_PHPCKS', '')
    if len(SHAREDRIVE_PHPCKS) == 0:
        SHAREDRIVE_PHPCKS = ''

    XSRF_TOKEN = environ.get('XSRF_TOKEN', '')
    if len(XSRF_TOKEN) == 0:
        XSRF_TOKEN = ''

    laravel_session = environ.get('laravel_session', '')
    if len(laravel_session) == 0:
        laravel_session = ''

    MIRROR_LOG_URL = environ.get('MIRROR_LOG_URL', '')
    if len(MIRROR_LOG_URL) == 0:    
        MIRROR_LOG_URL = ''

    LEECH_LOG_URL = environ.get('LEECH_LOG_URL', '')
    if len(LEECH_LOG_URL) == 0: 
        LEECH_LOG_URL = ''

    TIME_GAP = environ.get('TIME_GAP', '')
    if len(TIME_GAP) == 0:  
        TIME_GAP = -1
    else:   
        TIME_GAP = int(TIME_GAP)

    AUTHOR_NAME = environ.get('AUTHOR_NAME', '')
    if len(AUTHOR_NAME) == 0:   
        AUTHOR_NAME = 'WZML'

    AUTHOR_URL = environ.get('AUTHOR_URL', '')
    if len(AUTHOR_URL) == 0:    
        AUTHOR_URL = 'https://t.me/WeebZone_updates'

    TITLE_NAME = environ.get('TITLE_NAME', '')
    if len(TITLE_NAME) == 0:    
        TITLE_NAME = 'WeebZone'

    GD_INFO = environ.get('GD_INFO', '')
    if len(GD_INFO) == 0:   
        GD_INFO = 'Uploaded by WeebZone Mirror Bot'

    CREDIT_NAME = environ.get('CREDIT_NAME', '')
    if len(CREDIT_NAME) == 0:   
        CREDIT_NAME = 'WeebZone'

    NAME_FONT = environ.get('NAME_FONT', '')
    if len(NAME_FONT) == 0: 
        NAME_FONT = 'code'

    CAPTION_FONT = environ.get('CAPTION_FONT', '')
    if len(CAPTION_FONT) == 0:  
        CAPTION_FONT = 'code'

    DEF_IMDB_TEMP  = environ.get('IMDB_TEMPLATE', '')
    if len(DEF_IMDB_TEMP) == 0:
        DEF_IMDB_TEMP = '''<b>Title: </b> {title} [{year}]
    <b>Also Known As:</b> {aka}
    <b>Rating ⭐️:</b> <i>{rating}</i>
    <b>Release Info: </b> <a href="{url_releaseinfo}">{release_date}</a>
    <b>Genre: </b>{genres}
    <b>IMDb URL:</b> {url}
    <b>Language: </b>{languages}
    <b>Country of Origin : </b> {countries}

    <b>Story Line: </b><code>{plot}</code>

    <a href="{url_cast}">Read More ...</a>'''


    DEF_ANI_TEMP  = environ.get('ANIME_TEMPLATE', '')
    if len(DEF_ANI_TEMP) == 0:
        DEF_ANI_TEMP = """<b>{ro_title}</b>({na_title})
    <b>Format</b>: <code>{format}</code>
    <b>Status</b>: <code>{status}</code>
    <b>Start Date</b>: <code>{startdate}</code>
    <b>End Date</b>: <code>{enddate}</code>
    <b>Season</b>: <code>{season}</code>
    <b>Country</b>: {country}
    <b>Episodes</b>: <code>{episodes}</code>
    <b>Duration</b>: <code>{duration}</code>
    <b>Average Score</b>: <code>{avgscore}</code>
    <b>Genres</b>: {genres}
    <b>Hashtag</b>: {hashtag}
    <b>Studios</b>: {studios}

    <b>Description</b>: <i>{description}</i>"""

    FINISHED_PROGRESS_STR = environ.get('FINISHED_PROGRESS_STR', '')
    UN_FINISHED_PROGRESS_STR = environ.get('UN_FINISHED_PROGRESS_STR', '')
    MULTI_WORKING_PROGRESS_STR = environ.get('MULTI_WORKING_PROGRESS_STR', '')
    MULTI_WORKING_PROGRESS_STR = MULTI_WORKING_PROGRESS_STR.split(' ')
    if len(FINISHED_PROGRESS_STR) == 0 or len(FINISHED_PROGRESS_STR) == 0 or len(MULTI_WORKING_PROGRESS_STR) == 0:
        FINISHED_PROGRESS_STR = '█' # '■'
        UN_FINISHED_PROGRESS_STR = '▒' # '□'
        MULTI_WORKING_PROGRESS_STR = '▁ ▂ ▃ ▄ ▅ ▆ ▇'.split(' ')

    CHANNEL_USERNAME = environ.get('CHANNEL_USERNAME', '')
    if len(CHANNEL_USERNAME) == 0:
        CHANNEL_USERNAME = 'WeebZone_updates'

    FSUB_CHANNEL_ID = environ.get('FSUB_CHANNEL_ID', '')
    if len(FSUB_CHANNEL_ID) == 0:
        FSUB_CHANNEL_ID = '-1001512307861'

    IMAGE_URL = environ.get('IMAGE_URL', '')
    if len(IMAGE_URL) == 0:
        IMAGE_URL = 'https://graph.org/file/6b22ef7b8a733c5131d3f.jpg'

    TIMEZONE = environ.get('TIMEZONE', '')
    if len(TIMEZONE) == 0:
        TIMEZONE = 'Asia/Kolkata'

    PIXABAY_API_KEY = environ.get('PIXABAY_API_KEY', '')
    if len(PIXABAY_API_KEY) == 0:
        PIXABAY_API_KEY = ''

    PIXABAY_CATEGORY = environ.get('PIXABAY_CATEGORY', '')
    if len(PIXABAY_CATEGORY) == 0:
        PIXABAY_CATEGORY = ''

    PIXABAY_SEARCH = environ.get('PIXABAY_SEARCH', '')
    if len(PIXABAY_SEARCH) == 0:
        PIXABAY_SEARCH = ''

    WALLFLARE_SEARCH = environ.get('WALLFLARE_SEARCH', '')
    if len(WALLFLARE_SEARCH) == 0:
        WALLFLARE_SEARCH = ''

    WALLTIP_SEARCH = environ.get('WALLTIP_SEARCH', '')
    if len(WALLTIP_SEARCH) == 0:
        WALLTIP_SEARCH = ''

    WALLCRAFT_CATEGORY = environ.get('WALLCRAFT_CATEGORY', '')
    if len(WALLCRAFT_CATEGORY) == 0:
        WALLCRAFT_CATEGORY = ''

    PICS = (environ.get('PICS', '')).split()

    YT_DLP_QUALITY = environ.get('YT_DLP_QUALITY', '')
    if len(YT_DLP_QUALITY) == 0:
        YT_DLP_QUALITY = ''

    BASE_URL = environ.get('BASE_URL', '').rstrip("/")
    if len(BASE_URL) == 0:
        BASE_URL = ''
        srun(["pkill", "-9", "-f", "gunicorn"])
    else:
        srun(["pkill", "-9", "-f", "gunicorn"])
        Popen(f"gunicorn web.wserver:app --bind 0.0.0.0:{SERVER_PORT}", shell=True)

    initiate_search_tools()

    config_dict.update({'AS_DOCUMENT': AS_DOCUMENT,
                        'AUTHORIZED_CHATS': AUTHORIZED_CHATS,
                        'AUTO_DELETE_MESSAGE_DURATION': AUTO_DELETE_MESSAGE_DURATION,
                        'AUTO_DELETE_UPLOAD_MESSAGE_DURATION': AUTO_DELETE_UPLOAD_MESSAGE_DURATION,
                        'BASE_URL': BASE_URL,
                        'BOT_TOKEN': BOT_TOKEN,
                        'DATABASE_URL': DATABASE_URL,
                        'DOWNLOAD_DIR': DOWNLOAD_DIR,
                        'OWNER_ID': OWNER_ID,
                        'CMD_PERFIX': CMD_PERFIX,
                        'EQUAL_SPLITS': EQUAL_SPLITS,
                        'EXTENSION_FILTER': EXTENSION_FILTER,
                        'GDRIVE_ID': GDRIVE_ID,
                        'IGNORE_PENDING_REQUESTS': IGNORE_PENDING_REQUESTS,
                        'INCOMPLETE_TASK_NOTIFIER': INCOMPLETE_TASK_NOTIFIER,
                        'INDEX_URL': INDEX_URL,
                        'IS_TEAM_DRIVE': IS_TEAM_DRIVE,
                        'TG_SPLIT_SIZE': TG_SPLIT_SIZE,
                        'MEGA_API_KEY': MEGA_API_KEY,
                        'MEGA_EMAIL_ID': MEGA_EMAIL_ID,
                        'MEGA_PASSWORD': MEGA_PASSWORD,
                        'USER_SESSION_STRING': USER_SESSION_STRING,                   
                        'RSS_CHAT_ID': RSS_CHAT_ID,
                        'RSS_COMMAND': RSS_COMMAND,
                        'RSS_DELAY': RSS_DELAY,
                        'SEARCH_API_LINK': SEARCH_API_LINK,
                        'SEARCH_LIMIT': SEARCH_LIMIT,
                        'SEARCH_PLUGINS': SEARCH_PLUGINS,
                        'SERVER_PORT': SERVER_PORT,
                        'STATUS_LIMIT': STATUS_LIMIT,
                        'STATUS_UPDATE_INTERVAL': STATUS_UPDATE_INTERVAL,
                        'STOP_DUPLICATE': STOP_DUPLICATE,
                        'SUDO_USERS': SUDO_USERS,
                        'TGH_THUMB': TGH_THUMB,
                        'TELEGRAM_API': TELEGRAM_API,
                        'TELEGRAM_HASH': TELEGRAM_HASH,
                        'TORRENT_TIMEOUT': TORRENT_TIMEOUT,
                        'UPSTREAM_REPO': UPSTREAM_REPO,
                        'UPSTREAM_BRANCH': UPSTREAM_BRANCH,
                        'UPDATE_PACKAGES': UPDATE_PACKAGES,
                        'UPTOBOX_TOKEN': UPTOBOX_TOKEN,
                        'USE_SERVICE_ACCOUNTS': USE_SERVICE_ACCOUNTS,
                        'VIEW_LINK': VIEW_LINK,
                        'LEECH_ENABLED': LEECH_ENABLED,
                        'MIRROR_ENABLED': MIRROR_ENABLED,
                        'WATCH_ENABLED': WATCH_ENABLED,
                        'CLONE_ENABLED': CLONE_ENABLED,
                        'ANILIST_ENABLED': ANILIST_ENABLED,
                        'WAYBACK_ENABLED': WAYBACK_ENABLED,
                        'MEDIAINFO_ENABLED': MEDIAINFO_ENABLED,
                        'SET_BOT_COMMANDS': SET_BOT_COMMANDS,
                        'BOT_PM': BOT_PM,
                        'FORCE_BOT_PM': FORCE_BOT_PM,
                        'LEECH_LOG': LEECH_LOG,
                        'LEECH_LOG_URL': LEECH_LOG_URL,
                        'LEECH_LOG_INDEXING': LEECH_LOG_INDEXING,
                        'PAID_SERVICE': PAID_SERVICE,
                        'MIRROR_LOGS': MIRROR_LOGS,
                        'MIRROR_LOG_URL': MIRROR_LOG_URL,
                        'LINK_LOGS': LINK_LOGS,
                        'TIMEZONE': TIMEZONE,
                        'TITLE_NAME': TITLE_NAME,
                        'AUTHOR_NAME': AUTHOR_NAME,
                        'AUTHOR_URL': AUTHOR_URL,
                        'GD_INFO': GD_INFO,
                        'FSUB': FSUB,
                        'CHANNEL_USERNAME': CHANNEL_USERNAME,
                        'FSUB_CHANNEL_ID': FSUB_CHANNEL_ID,
                        'SHORTENER': SHORTENER,
                        'SHORTENER_API': SHORTENER_API,
                        'UNIFIED_EMAIL': UNIFIED_EMAIL,
                        'UNIFIED_PASS': UNIFIED_PASS,
                        'GDTOT_CRYPT': GDTOT_CRYPT,
                        'HUBDRIVE_CRYPT': HUBDRIVE_CRYPT,
                        'KATDRIVE_CRYPT': KATDRIVE_CRYPT,
                        'DRIVEFIRE_CRYPT': DRIVEFIRE_CRYPT,
                        'SHAREDRIVE_PHPCKS': SHAREDRIVE_PHPCKS,
                        'XSRF_TOKEN': XSRF_TOKEN,
                        'laravel_session': laravel_session,
                        'TOTAL_TASKS_LIMIT': TOTAL_TASKS_LIMIT,
                        'USER_TASKS_LIMIT': USER_TASKS_LIMIT,
                        'STORAGE_THRESHOLD': STORAGE_THRESHOLD,
                        'TORRENT_DIRECT_LIMIT': TORRENT_DIRECT_LIMIT,
                        'ZIP_UNZIP_LIMIT': ZIP_UNZIP_LIMIT,
                        'CLONE_LIMIT': CLONE_LIMIT,
                        'LEECH_LIMIT': LEECH_LIMIT,
                        'MEGA_LIMIT': MEGA_LIMIT,
                        'TIME_GAP': TIME_GAP,
                        'FINISHED_PROGRESS_STR': FINISHED_PROGRESS_STR,
                        'UN_FINISHED_PROGRESS_STR': UN_FINISHED_PROGRESS_STR,
                        'MULTI_WORKING_PROGRESS_STR': MULTI_WORKING_PROGRESS_STR,
                        'EMOJI_THEME': EMOJI_THEME,
                        'SHOW_LIMITS_IN_STATS': SHOW_LIMITS_IN_STATS,
                        'TELEGRAPH_STYLE': TELEGRAPH_STYLE,
                        'CREDIT_NAME': CREDIT_NAME,
                        'WALLFLARE_SEARCH': WALLFLARE_SEARCH,
                        'WALLTIP_SEARCH': WALLTIP_SEARCH,
                        'WALLCRAFT_CATEGORY': WALLCRAFT_CATEGORY,
                        'PIXABAY_API_KEY': PIXABAY_API_KEY,
                        'PIXABAY_CATEGORY': PIXABAY_CATEGORY,
                        'PIXABAY_SEARCH': PIXABAY_SEARCH,
                        'NAME_FONT': NAME_FONT,
                        'CAPTION_FONT': CAPTION_FONT,
                        'DEF_IMDB_TEMP': DEF_IMDB_TEMP,
                        'DEF_ANI_TEMP': DEF_ANI_TEMP,
                        'DISABLE_DRIVE_LINK': DISABLE_DRIVE_LINK,
                        'SOURCE_LINK': SOURCE_LINK,
                        'START_BTN1_NAME': START_BTN1_NAME,
                        'START_BTN1_URL': START_BTN1_URL,
                        'START_BTN2_NAME': START_BTN2_NAME,
                        'START_BTN2_URL': START_BTN2_URL,
                        'BUTTON_FOUR_NAME': BUTTON_FOUR_NAME,
                        'BUTTON_FOUR_URL': BUTTON_FOUR_URL,
                        'BUTTON_FIVE_NAME': BUTTON_FIVE_NAME,
                        'BUTTON_FIVE_URL': BUTTON_FIVE_URL,
                        'BUTTON_SIX_NAME': BUTTON_SIX_NAME,
                        'BUTTON_SIX_URL': TELEGRAPH_STYLE,
                        'WEB_PINCODE': WEB_PINCODE,
                        'YT_DLP_QUALITY': YT_DLP_QUALITY})


    if DATABASE_URL:
        DbManger().update_config(config_dict)

def get_buttons(key=None, edit_type=None):
    buttons = ButtonMaker()
    if key is None:
        buttons.sbutton('Edit Variables', "botset var")
        buttons.sbutton('Private Files', "botset private")
        buttons.sbutton('Qbit Settings', "botset qbit")
        buttons.sbutton('Aria2c Settings', "botset aria")
        buttons.sbutton('Close', "botset close")
        msg = 'Bot Settings:'
    elif key == 'var':
        alpha_config = OrderedDict(sorted(config_dict.items()))
        for k in list(alpha_config.keys())[START:10+START]:
            buttons.sbutton(k, f"botset editvar {k}")
        if STATE == 'view':
            buttons.sbutton('Edit', "botset edit var")
        else:
            buttons.sbutton('View', "botset view var")
        buttons.sbutton('Back', "botset back")
        buttons.sbutton('Close', "botset close")
        for x in range(0, len(config_dict)-1, 10):
            buttons.sbutton(int(x/10), f"botset start var {x}", position='footer')
        msg = f'Bot Variables. Page: {int(START/10)}. State: {STATE}'
    elif key == 'private':
        buttons.sbutton('Back', "botset back")
        buttons.sbutton('Close', "botset close")
        msg = 'Send private file: config.env, token.pickle, accounts.zip, list_drives.txt, cookies.txt or .netrc.' \
              '\nTo delete private file send the name of the file only as text message.\nTimeout: 60 sec'
    elif key == 'aria':
        for k in list(aria2_options.keys())[START:10+START]:
            buttons.sbutton(k, f"botset editaria {k}")
        if STATE == 'view':
            buttons.sbutton('Edit', "botset edit aria")
        else:
            buttons.sbutton('View', "botset view aria")
        buttons.sbutton('Add new key', "botset editaria newkey")
        buttons.sbutton('Back', "botset back")
        buttons.sbutton('Close', "botset close")
        for x in range(0, len(aria2_options)-1, 10):
            buttons.sbutton(int(x/10), f"botset start aria {x}", position='footer')
        msg = f'Aria2c Options. Page: {int(START/10)}. State: {STATE}'
    elif key == 'qbit':
        for k in list(qbit_options.keys())[START:10+START]:
            buttons.sbutton(k, f"botset editqbit {k}")
        if STATE == 'view':
            buttons.sbutton('Edit', "botset edit qbit")
        else:
            buttons.sbutton('View', "botset view qbit")
        buttons.sbutton('Back', "botset back")
        buttons.sbutton('Close', "botset close")
        for x in range(0, len(qbit_options)-1, 10):
            buttons.sbutton(int(x/10), f"botset start qbit {x}", position='footer')
        msg = f'Qbittorrent Options. Page: {int(START/10)}. State: {STATE}'
    elif edit_type == 'editvar':
        buttons.sbutton('Back', "botset back var")
        if key not in ['TELEGRAM_HASH', 'TELEGRAM_API', 'OWNER_ID', 'BOT_TOKEN']:
            buttons.sbutton('Default', f"botset resetvar {key}")
        buttons.sbutton('Close', "botset close")
        msg = f'Send a valid value for {key}. Timeout: 60 sec'
    elif edit_type == 'editaria':
        buttons.sbutton('Back', "botset back aria")
        if key != 'newkey':
            buttons.sbutton('Default', f"botset resetaria {key}")
            buttons.sbutton('Empty String', f"botset emptyaria {key}")
        buttons.sbutton('Close', "botset close")
        if key == 'newkey':
            msg = 'Send a key with value. Example: https-proxy-user:value'
        else:
            msg = f'Send a valid value for {key}. Timeout: 60 sec'
    elif edit_type == 'editqbit':
        buttons.sbutton('Back', "botset back qbit")
        buttons.sbutton('Empty String', f"botset emptyqbit {key}")
        buttons.sbutton('Close', "botset close")
        msg = f'Send a valid value for {key}. Timeout: 60 sec'
    if key is None:
        button = buttons.build_menu(1)
    else:
        button = buttons.build_menu(2)
    return msg, button

def update_buttons(message, key=None, edit_type=None):
    msg, button = get_buttons(key, edit_type)
    editMessage(msg, message, button)

def edit_variable(update, context, omsg, key):
    handler_dict[omsg.chat.id] = False
    value = update.message.text
    if value.lower() == 'true':
        value = True
    elif value.lower() == 'false':
        value = False
        if key == 'INCOMPLETE_TASK_NOTIFIER' and DATABASE_URL:
            DbManger().trunc_table('tasks')
    elif key == 'DOWNLOAD_DIR':
        if not value.endswith('/'):
            value = f'{value}/'
    elif key == 'STATUS_UPDATE_INTERVAL':
        value = int(value)
        if len(download_dict) != 0:
            with status_reply_dict_lock:
                if Interval:
                    Interval[0].cancel()
                    Interval.clear()
                    Interval.append(setInterval(value, update_all_messages))
    elif key == 'TORRENT_TIMEOUT':
        value = int(value)
        downloads = aria2.get_downloads()
        if downloads:
            aria2.set_options({'bt-stop-timeout': f'{value}'}, downloads)
        aria2_options['bt-stop-timeout'] = f'{value}'
    elif key == 'TG_SPLIT_SIZE':
        value = min(int(value), tgBotMaxFileSize)
    elif key == 'SERVER_PORT':
        value = int(value)
        srun(["pkill", "-9", "-f", "gunicorn"])
        Popen(f"gunicorn web.wserver:app --bind 0.0.0.0:{value}", shell=True)
    elif key == 'EXTENSION_FILTER':
        fx = value.split()
        GLOBAL_EXTENSION_FILTER.clear()
        GLOBAL_EXTENSION_FILTER.append('.aria2')
        for x in fx:
            GLOBAL_EXTENSION_FILTER.append(x.strip().lower())
    elif key in ['SEARCH_PLUGINS', 'SEARCH_API_LINK']:
        initiate_search_tools()
    elif key == 'GDRIVE_ID':
        if DRIVES_NAMES and DRIVES_NAMES[0] == 'Main':
            DRIVES_IDS[0] = value
        else:
            DRIVES_IDS.insert(0, value)
    elif key == 'INDEX_URL':
        if DRIVES_NAMES and DRIVES_NAMES[0] == 'Main':
            INDEX_URLS[0] = value
        else:
            INDEX_URLS.insert(0, value)
    elif value.isdigit():
        value = int(value)
    config_dict[key] = value
    update_buttons(omsg, 'var')
    update.message.delete()
    if DATABASE_URL:
        DbManger().update_config({key: value})

def edit_aria(update, context, omsg, key):
    handler_dict[omsg.chat.id] = False
    value = update.message.text
    if key == 'newkey':
        key, value = [x.strip() for x in value.split(':', 1)]
    elif value.lower() == 'true':
        value = "true"
    elif value.lower() == 'false':
        value = "false"
    if key in aria2c_global:
        aria2.set_global_options({key: value})
    else:
        downloads = aria2.get_downloads()
        if downloads:
            aria2.set_options({key: value}, downloads)
    aria2_options[key] = value
    update_buttons(omsg, 'aria')
    update.message.delete()
    if DATABASE_URL:
        DbManger().update_aria2(key, value)

def edit_qbit(update, context, omsg, key):
    handler_dict[omsg.chat.id] = False
    value = update.message.text
    if value.lower() == 'true':
        value = True
    elif value.lower() == 'false':
        value = False
    elif key == 'max_ratio':
        value = float(value)
    elif value.isdigit():
        value = int(value)
    client = get_client()
    client.app_set_preferences({key: value})
    qbit_options[key] = value
    update_buttons(omsg, 'qbit')
    update.message.delete()
    if DATABASE_URL:
        DbManger().update_qbittorrent(key, value)

def update_private_file(update, context, omsg):
    handler_dict[omsg.chat.id] = False
    message = update.message
    if not message.document and message.text:
        file_name = message.text
        fn = file_name.rsplit('.zip', 1)[0]
        if ospath.exists(fn):
            remove(fn)
        if fn == 'accounts':
            config_dict['USE_SERVICE_ACCOUNTS'] = False
            if DATABASE_URL:
                DbManger().update_config({'USE_SERVICE_ACCOUNTS': False})
        update.message.delete()
    else:
        doc = update.message.document
        file_name = doc.file_name
        doc.get_file().download(custom_path=file_name)
        if file_name == 'accounts.zip':
            if ospath.exists('accounts'):
                srun(["rm", "-rf", "accounts"])
            srun(["unzip", "-q", "-o", "accounts.zip", "-x", "accounts/emails.txt"])
            srun(["chmod", "-R", "777", "accounts"])
        elif file_name == 'list_drives.txt':
            DRIVES_IDS.clear()
            DRIVES_NAMES.clear()
            INDEX_URLS.clear()
            if GDRIVE_ID := config_dict['GDRIVE_ID']:
                DRIVES_NAMES.append("Main")
                DRIVES_IDS.append(GDRIVE_ID)
                INDEX_URLS.append(config_dict['INDEX_URL'])
            with open('list_drives.txt', 'r+') as f:
                lines = f.readlines()
                for line in lines:
                    temp = line.strip().split()
                    DRIVES_IDS.append(temp[1])
                    DRIVES_NAMES.append(temp[0].replace("_", " "))
                    if len(temp) > 2:
                        INDEX_URLS.append(temp[2])
                    else:
                        INDEX_URLS.append('')
        elif file_name in ['.netrc', 'netrc']:
            if file_name == 'netrc':
                rename('netrc', '.netrc')
                file_name = '.netrc'
            srun(["cp", ".netrc", "/root/.netrc"])
            srun(["chmod", "600", ".netrc"])
        elif file_name == 'config.env':
            load_dotenv('config.env', override=True)
            load_config()
        if '@github.com' in config_dict['UPSTREAM_REPO']:
            buttons = ButtonMaker()
            msg = 'Push to UPSTREAM_REPO ?'
            buttons.sbutton('Yes!', f"botset push {file_name}")
            buttons.sbutton('No', "botset close")
            sendMarkup(msg, context.bot, update.message, buttons.build_menu(2))
        else:
            update.message.delete()
    update_buttons(omsg)
    if DATABASE_URL and file_name != 'config.env':
        DbManger().update_private_file(file_name)
    if ospath.exists('accounts.zip'):
        remove('accounts.zip')

@new_thread
def edit_bot_settings(update, context):
    query = update.callback_query
    message = query.message
    user_id = query.from_user.id
    data = query.data
    data = data.split()
    if not CustomFilters.owner_query(user_id):
        query.answer(text="You don't have premision to use these buttons!", show_alert=True)
    elif data[1] == 'close':
        query.answer()
        handler_dict[message.chat.id] = False
        query.message.delete()
        query.message.reply_to_message.delete()
    elif data[1] == 'back':
        query.answer()
        handler_dict[message.chat.id] = False
        key = data[2] if len(data) == 3 else None
        update_buttons(message, key)
    elif data[1] in ['var', 'aria', 'qbit']:
        query.answer()
        update_buttons(message, data[1])
    elif data[1] == 'resetvar':
        query.answer()
        handler_dict[message.chat.id] = False
        value = ''
        if data[2] in default_values:
            value = default_values[data[2]]
            if data[2] == "STATUS_UPDATE_INTERVAL" and len(download_dict) != 0:
                with status_reply_dict_lock:
                    if Interval:
                        Interval[0].cancel()
                        Interval.clear()
                        Interval.append(setInterval(value, update_all_messages))
        elif data[2] == 'EXTENSION_FILTER':
            GLOBAL_EXTENSION_FILTER.clear()
            GLOBAL_EXTENSION_FILTER.append('.aria2')
        elif data[2] == 'TORRENT_TIMEOUT':
            downloads = aria2.get_downloads()
            if downloads:
                aria2.set_options({'bt-stop-timeout': '0'}, downloads)
            aria2_options['bt-stop-timeout'] = '0'
        elif data[2] == 'BASE_URL':
            srun(["pkill", "-9", "-f", "gunicorn"])
        elif data[2] == 'SERVER_PORT':
            value = 80
            srun(["pkill", "-9", "-f", "gunicorn"])
            Popen("gunicorn web.wserver:app --bind 0.0.0.0:80", shell=True)
        elif data[2] == 'GDRIVE_ID':
            if DRIVES_NAMES and DRIVES_NAMES[0] == 'Main':
                DRIVES_NAMES.pop(0)
                DRIVES_IDS.pop(0)
                INDEX_URLS.pop(0)
        elif data[2] == 'INDEX_URL':
            if DRIVES_NAMES and DRIVES_NAMES[0] == 'Main':
                INDEX_URLS[0] = ''
        elif data[2] == 'INCOMPLETE_TASK_NOTIFIER' and DATABASE_URL:
            DbManger().trunc_table('tasks')
        config_dict[data[2]] = value
        update_buttons(message, 'var')
        if DATABASE_URL:
            DbManger().update_config({data[2]: value})
    elif data[1] == 'resetaria':
        handler_dict[message.chat.id] = False
        aria2_defaults = aria2.client.get_global_option()
        if aria2_defaults[data[2]] == aria2_options[data[2]]:
            query.answer(text='Value already same as you added in aria.sh!')
            return
        query.answer()
        value = aria2_defaults[data[2]]
        aria2_options[data[2]] = value
        update_buttons(message, 'aria')
        downloads = aria2.get_downloads()
        if downloads:
            aria2.set_options({data[2]: value}, downloads)
        if DATABASE_URL:
            DbManger().update_aria2(data[2], value)
    elif data[1] == 'emptyaria':
        query.answer()
        handler_dict[message.chat.id] = False
        aria2_options[data[2]] = ''
        update_buttons(message, 'aria')
        downloads = aria2.get_downloads()
        if downloads:
            aria2.set_options({data[2]: ''}, downloads)
        if DATABASE_URL:
            DbManger().update_aria2(data[2], '')
    elif data[1] == 'emptyqbit':
        query.answer()
        handler_dict[message.chat.id] = False
        client = get_client()
        client.app_set_preferences({data[2]: value})
        qbit_options[data[2]] = ''
        update_buttons(message, 'qbit')
        if DATABASE_URL:
            DbManger().update_qbittorrent(data[2], '')
    elif data[1] == 'private':
        query.answer()
        if handler_dict.get(message.chat.id):
            handler_dict[message.chat.id] = False
            sleep(0.5)
        start_time = time()
        handler_dict[message.chat.id] = True
        update_buttons(message, 'private')
        partial_fnc = partial(update_private_file, omsg=message)
        file_handler = MessageHandler(filters=(Filters.document | Filters.text) & Filters.chat(message.chat.id) & Filters.user(user_id), callback=partial_fnc, run_async=True)
        dispatcher.add_handler(file_handler)
        while handler_dict[message.chat.id]:
            if time() - start_time > 60:
                handler_dict[message.chat.id] = False
                update_buttons(message)
        dispatcher.remove_handler(file_handler)
    elif data[1] == 'editvar' and STATE == 'edit':
        if data[2] in ['SUDO_USERS', 'IGNORE_PENDING_REQUESTS', 'CMD_PERFIX', 'OWNER_ID',
                       'USER_SESSION_STRING', 'TELEGRAM_HASH', 'TELEGRAM_API', 'AUTHORIZED_CHATS', 'RSS_DELAY'
                       'DATABASE_URL', 'BOT_TOKEN', 'DOWNLOAD_DIR', 'MIRROR_LOGS', 'LINK_LOGS', 'LEECH_LOG']:
            query.answer(text='Restart required for this edit to take effect!', show_alert=True)
        else:
            query.answer()
        if handler_dict.get(message.chat.id):
            handler_dict[message.chat.id] = False
            sleep(0.5)
        start_time = time()
        handler_dict[message.chat.id] = True
        update_buttons(message, data[2], data[1])
        partial_fnc = partial(edit_variable, omsg=message, key=data[2])
        value_handler = MessageHandler(filters=Filters.text & Filters.chat(message.chat.id) & Filters.user(user_id),
                                       callback=partial_fnc, run_async=True)
        dispatcher.add_handler(value_handler)
        while handler_dict[message.chat.id]:
            if time() - start_time > 60:
                handler_dict[message.chat.id] = False
                update_buttons(message, 'var')
        dispatcher.remove_handler(value_handler)
    elif data[1] == 'editvar' and STATE == 'view':
        value = config_dict[data[2]]
        if len(str(value)) > 200:
            query.answer()
            filename = f"{data[2]}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f'{value}')
            sendFile(context.bot, message, filename)
            return
        elif value == '':
            value = None
        query.answer(text=f'{value}', show_alert=True)
    elif data[1] == 'editaria' and (STATE == 'edit' or data[2] == 'newkey'):
        query.answer()
        if handler_dict.get(message.chat.id):
            handler_dict[message.chat.id] = False
            sleep(0.5)
        start_time = time()
        handler_dict[message.chat.id] = True
        update_buttons(message, data[2], data[1])
        partial_fnc = partial(edit_aria, omsg=message, key=data[2])
        value_handler = MessageHandler(filters=Filters.text & Filters.chat(message.chat.id) &
                        (CustomFilters.owner_filter | CustomFilters.sudo_user), callback=partial_fnc, run_async=True)
        dispatcher.add_handler(value_handler)
        while handler_dict[message.chat.id]:
            if time() - start_time > 60:
                handler_dict[message.chat.id] = False
                update_buttons(message, 'aria')
        dispatcher.remove_handler(value_handler)
    elif data[1] == 'editaria' and STATE == 'view':
        value = aria2_options[data[2]]
        if len(value) > 200:
            query.answer()
            filename = f"{data[2]}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f'{value}')
            sendFile(context.bot, message, filename)
            return
        elif value == '':
            value = None
        query.answer(text=f'{value}', show_alert=True)
    elif data[1] == 'editqbit' and STATE == 'edit':
        query.answer()
        if handler_dict.get(message.chat.id):
            handler_dict[message.chat.id] = False
            sleep(0.5)
        start_time = time()
        handler_dict[message.chat.id] = True
        update_buttons(message, data[2], data[1])
        partial_fnc = partial(edit_qbit, omsg=message, key=data[2])
        value_handler = MessageHandler(filters=Filters.text & Filters.chat(message.chat.id) &
                        (CustomFilters.owner_filter | CustomFilters.sudo_user), callback=partial_fnc, run_async=True)
        dispatcher.add_handler(value_handler)
        while handler_dict[message.chat.id]:
            if time() - start_time > 60:
                handler_dict[message.chat.id] = False
                update_buttons(message, 'var')
        dispatcher.remove_handler(value_handler)
    elif data[1] == 'editqbit' and STATE == 'view':
        value = qbit_options[data[2]]
        if len(str(value)) > 200:
            query.answer()
            filename = f"{data[2]}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f'{value}')
            sendFile(context.bot, message, filename)
            return
        elif value == '':
            value = None
        query.answer(text=f'{value}', show_alert=True)
    elif data[1] == 'edit':
        query.answer()
        globals()['STATE'] = 'edit'
        update_buttons(message, data[2])
    elif data[1] == 'view':
        query.answer()
        globals()['STATE'] = 'view'
        update_buttons(message, data[2])
    elif data[1] == 'start':
        query.answer()
        if START != int(data[3]):
            globals()['START'] = int(data[3])
            update_buttons(message, data[2])
    elif data[1] == 'push':
        query.answer()
        filename = data[2].rsplit('.zip', 1)[0]
        if ospath.exists(filename):
            srun([f"git add -f {filename} \
                    && git commit -sm botsettings -q \
                    && git push origin {config_dict['UPSTREAM_BRANCH']} -q"], shell=True)
        else:
            srun([f"git rm -r --cached {filename} \
                    && git commit -sm botsettings -q \
                    && git push origin {config_dict['UPSTREAM_BRANCH']} -q"], shell=True)
        query.message.delete()
        query.message.reply_to_message.delete()


def bot_settings(update, context):
    msg, button = get_buttons()
    sendMarkup(msg, context.bot, update.message, button)


bot_settings_handler = CommandHandler(BotCommands.BotSetCommand, bot_settings,
                                      filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
bb_set_handler = CallbackQueryHandler(edit_bot_settings, pattern="botset", run_async=True)

dispatcher.add_handler(bot_settings_handler)
dispatcher.add_handler(bb_set_handler)
