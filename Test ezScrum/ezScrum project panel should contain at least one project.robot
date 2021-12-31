*** Settings ***
Library    SeleniumLibrary

*** Test Cases ***
ezScrum project panel should contain at least one project
    Login With User Account And Password    ${account}    ${password}
    Project Panel Should Be Visibe
    Project Panel Should Contain At Least One Project

*** Keywords ***
Login With User Account And Password
    [Arguments]    ${account}    ${password}
    Wait Until Element Is Visible    xpath://*[@name='userId']    timeout=3s    error=Account field should be visible.
    Input Text    xpath://*[@name='userId']    ${account}
    Wait Until Element Is Visible    xpath://*[@name='password']    timeout=3s    error=Password field should be visible.
    Input Text    xpath://*[@name='password']    ${password}
    Wait Until Element Is Visible    id:Next    timeout=3s    error=Submit button should be visible.
    Click Element    id:Next

Project Panel Should Be Visibe
    Wait Until Element Is Visible    id:Projects_GirdPanel    timeout=3s    error=Project panel should be visible.

Project Panel Should Contain At Least One Project
    Wait Until Element Is Visible    xpath://*[@id='Projects_GirdPanel']//*[contains(@class, 'grid') and contains(@class, 'body')]/*[contains(@class, 'row')]    timeout=3s    error=Project panel should have project.

*** Variables ***
${account} =    xxxxxxx
${password} =    xxxxxxx