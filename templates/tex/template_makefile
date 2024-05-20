#!/usr/bin/env bash

# LATEX/PANDOC DOCKER SWITCH
# if docker images are set up for running latex, revert to those.  Otherwise 
# invoke latexmk/docker natively
# (LATEX_PREFIX is either "${LATEX_DOCKER} " or empty)
LATEX_DOCKER		:= texdock
LATEX_PREFIX		:= $(shell which ${LATEX_DOCKER} >/dev/null && echo "${LATEX_DOCKER} ")
LATEX				:= ${LATEX_PREFIX} latexmk

TEX_ENGINE			:= -_T_TEX_ENGINE_T_


############################################################
# VARIABLES
############################################################

SRC_TEX				:= $(wildcard _T_DIR_SRC_T_/*/*.tex)
DIR_TEX_OUT			:= _T_DIR_TEXMK_OUT_T_


############################################################
# TARGETS
############################################################

all: _T_DOC_NAME_T_.pdf

_T_DOC_NAME_T_.pdf:	${SRC_TEX} include_chapters
	@echo "Creating the document..."
	${LATEX} -output-directory=${DIR_TEX_OUT} -_T_TEX_ENGINE_T_ _T_FILE_TEX_MAIN_BASE_T_.tex
	@cp ${DIR_TEX_OUT}/_T_FILE_TEX_MAIN_BASE_T_.pdf _T_DOC_NAME_T_.pdf

.PHONY: include_chapters
include_chapters:	${SRC_TEX}
	@echo "Scanning for chapters..."
	@python3 _T_SCRIPT_INCLUDE_CHAPTERS_T_

