#Собрать пакет datacentric-debuild
```bash
git clone https://github.com/DataCentricAlliance/debuilder.git
cd debuilder/debuilder
sudo apt-get install debhelper devscripts python-opster python-debian python-tz
./deb.py build
#пакет будет лежать в папке build
```

#Настройка окружения

```bash
#устанавливаем пакет datacentric-debuild
sudo apt-get install datacentric-debuild

#устанавливаем переменные окружения
export DEBEMAIL="i.ivanov@datacentric.ru"
export DEBFULLNAME="Ivan Ivanov"
export DEBREPOSITORY="example.repo.net:/opt/ubuntu/mini-dinstall/incoming/"
```

#Увеличить версию пакета
```bash
#добавили запись в changelog и собрали с новой версией
./deb.py build -v <maj|min|mntn|build> -m <message>

#changelog надо закоммитить (лучше вместе с остальными изменениями пакета)
git commit -a -m "теперь точно всё работает"

#мержим ветку через gitlab
git push origin ...

#кладём пакет в репозиторий
./deb.py pub
```

#Создание пакета

```bash
#создаём папку где будет лежать наш проект
mkdir mypackage
cd mkdir

#создаём папку debian, changelog и файл deb.py
#в папку debian нужно класть post/pre скрипты
mkdir debian
touch debian/changelog
touch deb.py
chmod a+x deb.py

#добавляем всё в git
git add *

#редактируем файл deb.py, смотреть "Описание deb.py"
vim deb.py
 
#добавляем запись в changelog и собираем пакет
./deb.py build -v min -m "Initial release"

#коммитим, проходим ревью, мёржим
git commit -a -m "add new package mypackage"

#отправляем пакет в репозиторий
./deb.py pub
```

#Описание deb.py

Пример:
```python
!/usr/bin/python

from facetz.utils.debuild import *

dispatch(
    Package(
        name = "mypackage",
        section = "facetz",
        description = "Tool that is never falls",
        depends = "python-pymongo",
        conflicts = "myoldpackage",

        commands = [Copy(["mypackage.*.cfg"], "/etc/mypackage/"),
                    EnvLink("/etc/mypackage/mypackage.$ENV.cfg", "/etc/mypackage/mypackage.cfg"),
                    Copy(["tool.py", "common.py"], "/opt/facetz/mypackage/")              
                    Mkdir("/var/log/facetz/mypackage")]
    )
)
```

* dispatch - нужен для разбора коммандной строки
* Package - класс содержащий описание пакета:
    * name - имя пакета
    * section - секция пакета https://www.debian.org/doc/debian-policy/ch-archive.html#s-subsections
    * description - описание пакета
    * depends - зависимости от других deb-пакетов
    * conflicts - конфликты с другими deb-пакетами
    * provides - для виртуальных пакетов
    * commands - команды сборщику пакета:
        * Copy(wildcards, dest) - копирует файлы/папки в dest. Если dest заканчивается на '/' то копирует в папку dest. Если dest не заканчивается '/' то считается что при копировании вы хотите переименовать файл и он будет скопирован в папку dirname(dest) и назван basename(dest)
        * Copy(["myconf.cfg"], "/etc/facetz/tool/tool.cfg") - файл myconf.cfg будет скопирован в папку /etc/facetz/tool и переименован в tool.cfg
        * Copy(["myconf.cfg"], "/etc/facetz/tool/") - файл myconf.cfg будет скопирован в папку /etc/facetz/tool и не будет переименован
        * Copy(["conf"], "/etc/facetz/tool") - если conf - это папка то она будет переименована в tool и скопирована в /etc/facetz
        * Mkdir(dir_name, user=root, group=root) - создаст папку dir_name, добавляет chown user:group dir в postrm скрипт

        * EnvLink(pattern, link_name=None) - Если у нас разные конфиги для каждого из окружений, к примеру tool.development.cfg, tool.testing.cfg, tool.production.cfg, чтобы не создавать три пакета с каждым из этих конфигов, можно использовать EnvLink. Для этого нужно положить все конфиги в один пакет командой Copy а затем создать ссылку на конфиг с помощью EnvLink.
        ```python
        #Для нашего примера
        Copy(["tool.*.cfg"], "/etc/facetz/tool/")
        EnvLink("/etc/facetz/tool/tool.$ENV.cfg", "/etc/facetz/tool/tool.cfg")
        ```
        EnvLink создаст символьную ссылку /etc/facetz/tool/tool.cfg -> /etc/facetz/tool/tool.development.cfg если на машине установлен пакет facetz-env-development или /etc/facetz/tool/tool.cfg -> /etc/facetz/tool/tool.production.cfg если на машине стоит пакет facetz-env-production. Таки образом мы можем в нашей программе использовать один путь для всех конфигов "/etc/facetz/too/tool.cfg", а какой именно конфиг будет подключем определяется созданной в момент установки пакета ссылкой.
        Как это работает? Есть пакеты окружения facez-env-development, facetz-env-testing, facetz-env-production и виртуальный пакет facetz-env. Каждый из них устанавливает на машину файл /etc/facetz/env/env.cfg который содержит одну строчку "development", "testing" или "production". На машине может стоять только один из них. Команда EnvLink добавляет в postinst скрипт две строки:
        ```bash
        ENV=$(cat /etc/facetz/env/env.cfg)
        ln -sf <pattern> <link_name>
        ```
        и в postrm скрипт:
        ```bash
        extra_portrm
        rm -rf <link_name>
        ```
    
    
