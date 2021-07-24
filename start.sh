#! /usr/bin/env bash

currentdir="${PWD##*/}"

if [ $currentdir != 'utilot' ]; then
    echo '[start:err] Please cd to the project root first'
    exit 1
fi

if [ "$1" = '--compile-speedups' ]; then
    if [ ! -d speedups ]; then
        echo '[start:err] Folder speedups does not exist'
        exit 1
    fi
    
    
    (cd speedups && cargo run --release)
    
    if [ $? != 0 ]; then
        echo '[start:err] Compilation failure'
        exit 1
    fi
    
    if [ ! -f speedups/target/release/libspeedups.so ]; then
        echo '[start:err] .so file not found'
        exit 1
    fi 
    
    cp speedups/target/release/libspeedups.so speedups.so
    echo '[start:ok] Successfully copied the .so file'

fi


if [ ! -f bot.py ]; then
    echo '[start:err] bot.py not found'
    exit 1
fi

python bot.py


    
