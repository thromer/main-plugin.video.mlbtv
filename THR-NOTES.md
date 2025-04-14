# My notes

## How it works as a plugin, independent of where it gets its data.
* autoplay (end of directory / caching is confusing) (mode=None)
  * play a specific stream (mode=102) (invokes directly, empty menu)


* categories (mode=None)
  * Today's Games mode=100 (uncached)
    * 'Yesterday'
	* Highlights (ok as a directory) (mode=900)
	* Each game via 
	  * `create_game_listitem` (which does a lot of work), `add_stream` 
	  * `create_linear_channel_listitem` 
	  * `create_big_inning_listitem`
	  * `create_game_changer_listitem` (mode 500)
	* 'Tomorrow'
  * Yesterday's Games mode=105
    * as for today's games
  * See Yesterday's Scores at inning mode=108
    * ??? via weird stuff (mode=101)
  * Goto Date mode=200
    * similar to today's games but with a dialog and weird failure mode
  * Minor League Games mode=109
    * TODO `minor_league_categories`
  * Featured Videos mode=300
    * TODO `featured_videos`

## Speeding up development
* run dev code *locally* not on chromecast
* dev mode where we just hard code a gamePk to autoplay (can't ever stop, though ...), or prompt whether to "autoplay"
* script sync to chromecast

## Potential optimizations / simplifications
* move almost all of main.py and service.py to resources/lib so we get pyc files (!). At least that's my theory.
* don't make wasted call to category if we ended up doing auto play
* get rid of kodisix
* use addListItems instead of multiple addListItem 
* I'm sure I tried this, but why can't autoplay directly call setResolvedUrl instead of having to go through another round of main?
  * maybe because as Roman\_V\_Msa [says](https://forum.kodi.tv/showthread.php?tid=375302&pid=3175803#pid3175803) "when playback is stopped/finished it needs to re-read the current virtual folder to refresh "in progress"/"watched" state for the current item.' Or maybe that explains other things
* Why doesn't reuselanguageinvoker help? (And what trouble will it cause?)
* IMO `create_game_listitem` is ugly and slow: user isn't navigating a tree, they're deciding how to play the item they've already chosen. So just use dialogs and don't cycle through stream. But then the UX is non-standard and you lose weird things you can choose from the context menu.
* Get rid of errors and warnings as much as possible

## Other cleanup
* 100 seems cacheable but it isn't, what's the concern?
* 101 comment says don't cache prev/next but that isn't what's happening
* Seems like various things that shouldn't be cached are left cacheable
* Why not INPUT_DATE in main.py mode 200 ?  Supported since forever. Pretty horrific UI, though

## Other things
* Should only have to call setContent once per invocation.
* Super helpful https://romanvm.github.io/Kodistubs/index.html

## Questions
* So this cache, does it have infinite TTL? [Apparently so](https://github.com/search?q=repo%3Axbmc%2Fxbmc%20path%3AGUI%20cachedItems.load&type=code). I see "if slow" means ["cache if the last time it took over 1000ms"](https://github.com/search?q=repo%3Axbmc%2Fxbmc+path%3AGUI+CacheToDiscIfSlow+&type=code) .  So better not to cache anything remotely dynamic.
* Do we get a whole new python binary every time?

## Suspicious
* endOfDirectory in the middle of mlb.py

# Chromebook

## Tips
[Keyboard shortcuts](https://kodi.wiki/view/Keyboard_controls)

## Startup sequence
For example, with debugging turned on, reasonably warmed up (highlights), some of the infos are from me
```
37.602 T:20550    info <general>: CBuiltins::Execute ActivateWindow(videos,"plugin://plugin.video.mlbtv-ted",return)
37.602 T:20550   debug <general>: Activating window ID: 10025
37.603 T:20550   debug <general>: ------ Window Init (Pointer.xml) ------
37.922 T:20550   debug <general>: ------ Window Deinit (Home.xml) ------
37.922 T:20550   debug <general>: FreeVisualisation() done
37.937 T:20550   debug <general>: ------ Window Init (MyVideoNav.xml) ------
37.939 T:20550   error <general>: Control 55 in window 10025 has been asked to focus, but it can't
37.956 T:20550   debug <general>: CGUIMediaWindow::GetDirectory (plugin://plugin.video.mlbtv-ted/)
37.956 T:20743   debug <general>: Thread waiting start, auto delete: false
37.959 T:20728   debug <general>: CAddonDatabase::SetLastUsed[plugin.video.mlbtv-ted] took 3 ms
37.959 T:20743    info <general>: CScriptInvocationManager::Execute /home/ted/.kodi/addons/plugin.video.mlbtv-ted/main.py
37.959 T:20743    info <general>: ILanguageInvoker::Execute /home/ted/.kodi/addons/plugin.video.mlbtv-ted/main.py
37.959 T:20744    info <general>: CLanguageInvokerThread::Execute
37.959 T:20744    info <general>: CPythonInvoker::Execute /home/ted/.kodi/addons/plugin.video.mlbtv-ted/main.py
37.959 T:20744    info <general>: ILanguageInvoker::Execute /home/ted/.kodi/addons/plugin.video.mlbtv-ted/main.py
37.959 T:20744    info <general>: CPythonInvoker(9, /home/ted/.kodi/addons/plugin.video.mlbtv-ted/main.py): start processing
37.971 T:20744   debug <general>: -->Python Interpreter Initialized<--
37.971 T:20744   debug <general>: CPythonInvoker(9, /home/ted/.kodi/addons/plugin.video.mlbtv-ted/main.py): the source file to load is "/home/ted/.
kodi/addons/plugin.video.mlbtv-ted/main.py"
di/addons/plugin.video.mlbtv-ted
37.971 T:20744   debug <general>: CPythonInvoker(9, /home/ted/.kodi/addons/plugin.video.mlbtv-ted/main.py): instantiating addon using automatically
 obtained id of "plugin.video.mlbtv-ted" dependent on version 3.0.0 of the xbmc.python api
37.985 T:20744    info <general>: THROMER enter main.py
```

# Build from source

As needed:
```
`cd ~/3p/xbmc/tools/depends && make distclean && ./bootstrap
```

## Chromebook

[Omega instructions](https://github.com/xbmc/xbmc/blob/Omega/docs/README.Linux.md)
* No need to build any dependencies from source (except optionally inputstream.adaptive addon)

Prerequisites / recommended

```shell
apt install -y ccache
apt install -y cmake
apt install -y autoconf automake autopoint gettext autotools-dev cmake curl gawk gdc gperf libass-dev libavahi-client-dev libavahi-common-dev libbluetooth-dev libbluray-dev libbz2-dev libcdio-dev libp8-platform-dev libcrossguid-dev libcwiid-dev libdbus-1-dev libegl1-mesa-dev libenca-dev libflac-dev libfontconfig-dev libfreetype6-dev libfribidi-dev libfstrcmp-dev libgcrypt-dev libgif-dev libglew-dev libgpg-error-dev libgtest-dev libiso9660-dev libjpeg-dev liblcms2-dev liblirc-dev libltdl-dev liblzo2-dev libmicrohttpd-dev libnfs-dev libogg-dev libomxil-bellagio-dev libpcre3-dev libplist-dev libpulse-dev libshairplay-dev libsmbclient-dev libspdlog-dev libsqlite3-dev libssl-dev libtinyxml-dev libtinyxml2-dev libtool libudev-dev libunistring-dev libva-dev libvdpau-dev libvorbis-dev libxkbcommon-dev libxmu-dev libxrandr-dev libxt-dev lsb-release meson nasm ninja-build python3-dev rapidjson-dev swig unzip uuid-dev zip zlib1g-dev libmariadb-dev
apt install -y flatbuffers-compiler
apt install -y libgnutls28-dev wipe
apt install -y libcurl4-openssl-dev
apt install -y flatbuffers-compiler-dev
apt install -y libflatbuffers-dev
apt install -y libtag1-dev
apt install libdrm-dev
apt install -y wayland-protocols
apt install -y waylandpp-dev
apt install -y libdisplay-info-dev
apt install -y libgbm-dev
apt install -y libinput-dev
apt install -y vainfo
```

Basically:
```
cd ~/3p
git clone --single-branch --branch Omega https://github.com/xbmc/xbmc
# I think this was an accident sudo make -C tools/depends/target/crossguid PREFIX=/usr/local
mkdir ~/kodi-build
cd ~/kodi-build
cmake ../3p/xbmc -DCMAKE_INSTALL_PREFIX=/usr/local -DCORE_PLATFORM_NAME="x11 wayland gbm" -DAPP_RENDER_SYSTEM=gl
cmake --build . -- VERBOSE=1 -j$(getconf _NPROCESSORS_ONLN)
sudo make install
```

Optionally:
```
sudo make -j$(getconf _NPROCESSORS_ONLN) -C tools/depends/target/binary-addons PREFIX=/usr/local ADDONS="inputstream.adaptive"
```

* obsolete: Either make inputstream.adaptive optional="true" in addon.xml or [build inputstream.adaptive](https://github.com/xbmc/inputstream.adaptive/wiki/How-to-build) and throw it in /usr/local/share/kodi/addons/

Run!
`kodi --windowing=x11`

## Android

**probably want --enable-debug=no**

https://developer.android.com/studio#command-line-tools-only

Also https://forum.kodi.tv/showthread.php?tid=378649&pid=3208198#pid3208198

Put it in ${ANDROID_HOME}/cmdline-tools/ AND move everything to latest

```
yes | sdkmanager --licenses
sdkmanager platform-tools
sdkmanager "platforms;android-35"
sdkmanager "build-tools;34.0.0"
sdkmanager "ndk;21.4.7075529"
keytool -genkey -keystore ~/.android/debug.keystore -v -alias androiddebugkey -dname "CN=Android Debug,O=Android,C=US" -keypass android -storepass android -keyalg RSA -keysize 2048 -validity 10000

sudo apt install -y autoconf bison build-essential curl default-jdk flex gawk git gperf lib32stdc++6 lib32z1 lib32z1-dev libcurl4-openssl-dev unzip zip zlib1g-dev
mkdir ~/android-tools
ln -s ~/Android/Sdk ~/android-tools/android-sdk-linux  # for convenient copy/pasted from build instructions
ln -s ~/3p/xbmc kodi
cd ~/kodi/tools/depends/
./bootstrap
```
### x86_64

Haven't gotten this working ...

```
./configure --with-tarballs=$HOME/android-tools/xbmc-tarballs --host=x86_64-linux-android --with-sdk-path=$HOME/android-tools/android-sdk-linux --prefix=$HOME/android-tools/xbmc-depends --with-ndk-path=$ANDROID_HOME/ndk/21.4.7075529
# make -j$(getconf _NPROCESSORS_ONLN) -C tools/depends/target/binary-addons ADDONS="inputstream.adaptive"
```

### CCWGTV (arm)
* Might need to hack up `${ANDROID_HOME}/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/include/time.h` [along these lines](https://lists.gnutls.org/pipermail/gnutls-devel/2024-November/026453.html) -- just comment it all out
* Definitely need to hack up `~/kodi/tools/depends/target/sqlite3/arm-linux-androideabi-21-debug/sqlite3.c` near line 36279 along [these lines](https://sqlite.org/src/info/f18b2524da6bbbcf)
* And `~/kodi/tools/depends/target/samba-gplv3/arm-linux-androideabi-21-debug/lib/util/charset/iconv.c` to remove definition of swab around line 763
* And `~/kodi/tools/depends/target/libcdio-gplv3/arm-linux-androideabi-21-debug/lib/driver/_cdio_stdio.c` to comment out lines 54, 55 so as not use fseeko
* And `~/kodi/CMakeLists.txt` to comment out TagLib, or maybe we should have configured with `--enable_internal_taglib=off` or something

```
./configure --with-tarballs=$HOME/android-tools/xbmc-tarballs --host=arm-linux-androideabi --with-sdk-path=$HOME/android-tools/android-sdk-linux --prefix=$HOME/android-tools/xbmc-depends --with-ndk-path=$ANDROID_HOME/ndk/21.4.7075529 -with-sdk=32  # for Android 12. Later maybe we can do 34 for Android 14 ... doesn't seem like this really helped but you wouldn't expect it to hurt, either.
make -j$(getconf _NPROCESSORS_ONLN)
cd ~/kodi
make -j$(getconf _NPROCESSORS_ONLN) -C tools/depends/target/binary-addons ADDONS="inputstream.adaptive"
mkdir $HOME/kodi-build-android-arm
make -C tools/depends/target/cmakebuildsys BUILD_DIR=$HOME/kodi-build-android-arm
cd $HOME/kodi-build-android-arm
make -j$(getconf _NPROCESSORS_ONLN)
make apk  # no target???
```

### Try again on neo
Also, no funky symlinks, just in case, so start with:

```
export ANDROID_HOME=${HOME}/android-tools/android-sdk-linux
mkdir -p ${ANDROID_HOME}
cd ${ANDROID_HOME}
unzip ~/Downloads/commandlinetools-linux-13114758_latest.zip
cd commandlinetools
mkdir latest
mv * latest
```

Maybe `ndk;23.2.8568313` will work better? Based on [this](ndk;23.2.8568313) and [ffmpeg-kit ndk compatibility](https://github.com/arthenica/ffmpeg-kit/wiki/NDK-Compatibility)

Or even more likely `ndk;21.4.7075529` per the link at the top of this section. But that's even worse at least on neo.

There's this but I don't know if it is canonical or what versions of stuff it uses ...

And this looks better though it doesn't get updated? 
https://github.com/xbmc/xbmc/tree/Omega/tools/buildsteps/android
