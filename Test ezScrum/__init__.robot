*** Settings ***
Library    SeleniumLibrary
Resource    ../keywords/common.txt

Suite Setup    Open ezScrum Page
Suite Teardown    Close Browser