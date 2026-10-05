%% Stripped-down version of puthesis_undergraduate.cls
%% (originally by Evan Papageorgiou, adapted from puthesis.cls).
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{puthesis_undergraduate}[2026/10/05 stripped]
\RequirePackage{setspace}

\def\advisor#1{\gdef\@advisor{#1}}
\def\submitted#1{\gdef\@submitted{#1}}
\def\@submitted{\today}
\def\@dept{}
\def\@deptpref{Department of}
\def\department#1{\gdef\@dept{#1}}
\def\departmentprefix#1{\gdef\@deptpref{#1}}
\long\def\acknowledgements#1{\gdef\@acknowledgements{#1}}
\long\def\@abstract{\@latex@error{No \noexpand\abstract given}\@ehc}

\newcommand*{\makelot}{}
\newcommand*{\makelof}{}
\DeclareOption{lot}{\renewcommand*{\makelot}{%
  \clearpage\addcontentsline{toc}{section}{List of Tables}\listoftables}}
\DeclareOption{lof}{\renewcommand*{\makelof}{%
  \clearpage\addcontentsline{toc}{section}{List of Figures}\listoffigures}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{report}}
\ProcessOptions
\LoadClass[12pt]{report}

\setlength{\oddsidemargin}{0.5in}
\setlength{\evensidemargin}{.1in}
\setlength{\topmargin}{-.5in}
\setlength{\textheight}{9in}
\setlength{\textwidth}{6.0in}

\long\def\abstract#1{\gdef\@abstract{#1}}

\def\authornotes#1{\gdef\@authornotes{#1}}
\newcommand{\maketitlepage}{{%
  \thispagestyle{empty}
  \begin{center}{\sc\LARGE \@title}\end{center}
  \vspace{.6in}
  \begin{center}{\sc \@author}
    \ifx\@advisor\undefined\else\\ Advisor: \@advisor\fi
    \ifx\@authornotes\undefined\else\\[1ex]{\small\singlespacing \@authornotes\par}\fi
  \end{center}
  \ifx\@dept\@empty\else
    \vspace{.6in}
    \begin{center}\@deptpref{} \@dept\\ Princeton University\end{center}
  \fi
  \vspace{0.9in}
  \begin{center}\@submitted\end{center}
  \clearpage}}

\newcommand*{\makeabstract}{%
  \addcontentsline{toc}{section}{Abstract}
  \begin{center}\Large\textbf{Abstract}\end{center}
  \@abstract\clearpage}

\def\makeacknowledgements{%
  \ifx\@acknowledgements\undefined\else
    \addcontentsline{toc}{section}{Acknowledgements}
    \begin{center}\Large\textbf{Acknowledgements}\end{center}
    \@acknowledgements\clearpage
  \fi}

\AddToHook{begindocument/end}{%
  \doublespacing
  \pagenumbering{roman}
  \maketitlepage\makeabstract\makeacknowledgements
  \tableofcontents\makelot\makelof
  \clearpage\pagenumbering{arabic}}
\endinput
