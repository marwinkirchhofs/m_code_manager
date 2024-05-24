#!/usr/bin/env bash

include _T_FILE_MAKE_VARIABLES_T_

#######################################
# BUILD
#######################################

.PHONY: build_debug
build_debug:	_T_DIR_BUILD_T_/_T_DIR_DEBUG_T_/_T_APP_NAME_T_

_T_DIR_BUILD_T_/_T_DIR_DEBUG_T_/_T_APP_NAME_T_:	${SRC}
	@cd _T_DIR_BUILD_T_/_T_DIR_DEBUG_T_ && cmake -DCMAKE_BUILD_TYPE=Debug ../..
	@make -C _T_DIR_BUILD_T_/_T_DIR_DEBUG_T_

.PHONY: build_release
build_release:	_T_DIR_BUILD_T_/_T_DIR_RELEASE_T_/_T_APP_NAME_T_

_T_DIR_BUILD_T_/_T_DIR_RELEASE_T_/_T_APP_NAME_T_:	${SRC}
	@cd _T_DIR_BUILD_T_/_T_DIR_RELEASE_T_ && cmake -DCMAKE_BUILD_TYPE=Release ../..
	@make -C _T_DIR_BUILD_T_/_T_DIR_RELEASE_T_

.PHONY: build_maxopt
build_maxopt:	_T_DIR_BUILD_T_/_T_DIR_MAXOPT_T_/_T_APP_NAME_T_

_T_DIR_BUILD_T_/_T_DIR_MAXOPT_T_/_T_APP_NAME_T_:	${SRC}
	@cd _T_DIR_BUILD_T_/_T_DIR_MAXOPT_T_ && cmake -DCMAKE_CXX_FLAGS="${DCMAKE_CXX_FLAGS} -Ofast -march=native" ../..
	@make -C _T_DIR_BUILD_T_/_T_DIR_MAXOPT_T_

#######################################
# RUN
#######################################

.PHONY: release
release:	build_release
	@cd _T_DIR_BUILD_T_/$@ && ./_T_APP_NAME_T_

.PHONY: debug
debug:		build_debug
	@cd _T_DIR_BUILD_T_/$@ && ./_T_APP_NAME_T_

.PHONY: maxopt
maxopt:		build_maxopt
	@cd _T_DIR_BUILD_T_/$@ && ./_T_APP_NAME_T_
