
# Install application
install(
    TARGETS GSI-RADS
    DESTINATION bin
)

# setup .desktop file
if (UNIX)
	set(APP_CONFIG_CONTENT "[Desktop Entry]
	Name=GSI-RADS
	Comment=GSI-RADS
	Exec=/opt/GSI-RADS/bin/GSI-RADS
	Terminal=false
	Type=Application
	#Icon=/opt/GSI-RADS/data/Icons/GSI-RADS_logo_large.png
	Categories=public.app-categorical.medical")

	# write
	file(WRITE ${PROJECT_BINARY_DIR}/GSI-RADS.desktop ${APP_CONFIG_CONTENT})

	# install
	install(
	    FILES ${PROJECT_BINARY_DIR}/GSI-RADS.desktop
	    DESTINATION /usr/share/applications/
	    PERMISSIONS OWNER_READ OWNER_EXECUTE OWNER_WRITE GROUP_READ GROUP_EXECUTE GROUP_WRITE WORLD_READ WORLD_WRITE WORLD_EXECUTE
	)
endif()

set(CPACK_PACKAGE_NAME "GSI-RADS")
set(CPACK_PACKAGE_CONTACT "Andre Pedersen andre.pedersen@sintef.no")
set(CPACK_PACKAGE_VENDOR "SINTEF")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "GSI-RADS is an open-source platform for ... created by SINTEF Medical Technology.")
#set(CPACK_PACKAGE_DESCRIPTION_FILE "${PROJECT_SOURCE_DIR}/README.md")
#set(CPACK_RESOURCE_FILE_LICENSE ${PROJECT_SOURCE_DIR}/LICENSE.md) # @TODO somehow concatenate all licences to this file..

set(CPACK_PACKAGE_VERSION_MAJOR "0")
set(CPACK_PACKAGE_VERSION_MINOR "1")
set(CPACK_PACKAGE_VERSION_PATCH "1")
set(CPACK_PACKAGE_FILE_NAME "GSI-RADS")
set(CPACK_COMPONENT_FAST_REQUIRED ON)

SET(CPACK_PACKAGE_EXECUTABLES "GSI-RADS" "GSI-RADS")

if(WIN32 AND NOT UNIX)
	
    ## Windows
    # Create windows installer (Requires NSIS from http://nsis.sourceforge.net)
    set(CPACK_GENERATOR NSIS)

	set(CPACK_PACKAGE_INSTALL_DIRECTORY "GSI-RADS")
	set(CPACK_PACKAGE_FILE_NAME "fastpathology_win10_v${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH}")
	set(CPACK_NSIS_ENABLE_UNINSTALL_BEFORE_INSTALL ON)
	set(CPACK_NSIS_MENU_LINKS "bin\\\\GSI-RADS.exe" "GSI-RADS")
	set(CPACK_CREATE_DESKTOP_LINKS "GSI-RADS")

	# Icon stuff
	set(CPACK_NSIS_MODIFY_PATH ON)
	#set(CPACK_NSIS_MUI_ICON ${PROJECT_SOURCE_DIR}/data/Icons/GSI-RADS_icon_large.ico)  # @TODO: find a way to add icon to installer
	#set(CPACK_NSIS_MUI_UNICON ${PROJECT_SOURCE_DIR}/data/Icons/GSI-RADS_icon_large.ico)
	#set(CPACK_CREATE_DESKTOP_LINKS ON)
	set(CPACK_NSIS_INSTALLED_ICON_NAME bin\\\\GSI-RADS.exe)
	set(CPACK_NSIS_INSTALL_DIRECTORY ${CPACK_NSIS_INSTALL_ROOT}/GSI-RADS) #${CPACK_PACKAGE_INSTALL_DIRECTORY})

    include(CPack)
else()
    ## UNIX

	# Get distro name and version
	find_program(LSB_RELEASE_EXEC lsb_release)
	execute_process(COMMAND ${LSB_RELEASE_EXEC} -is
			OUTPUT_VARIABLE DISTRO_NAME
			OUTPUT_STRIP_TRAILING_WHITESPACE
	)
	string(TOLOWER ${DISTRO_NAME} DISTRO_NAME)
	execute_process(COMMAND ${LSB_RELEASE_EXEC} -rs
			OUTPUT_VARIABLE DISTRO_VERSION
			OUTPUT_STRIP_TRAILING_WHITESPACE
	)

	if(APPLE)
		## Create Bundle (macOS)
		set(CPACK_GENERATOR "DragNDrop")

		set(CPACK_BUNDLE_NAME "GSI-RADS")
	else()
	    # Create debian package (Ubuntu Linux)
	    set(CPACK_GENERATOR "DEB")

	    # Select components to avoid some cmake leftovers from built dependencies
	    set(CPACK_DEB_COMPONENT_INSTALL OFF)
	    set(CPACK_PACKAGING_INSTALL_PREFIX "/opt/GSI-RADS")  #"/opt/")  $HOME/GSI-RADS
	    set(CPACK_DEBIAN_COMPRESSION_TYPE "xz")
		set(CPACK_DEBIAN_FILE_NAME "fastpathology_ubuntu_v${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH}.deb")
	    set(CPACK_DEBIAN_fastpathology_PACKAGE_NAME "GSI-RADS")
	endif()
    include(CPack)
endif()
