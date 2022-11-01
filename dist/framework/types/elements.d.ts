import { PropsUIPage } from './pages';
import { PropsUIPrompt } from './prompts';
export declare type PropsUI = PropsUIText | PropsUIButton | PropsUICheckBox | PropsUIRadioItem | PropsUISpinner | PropsUIHeader | PropsUITable | PropsUISearchBar | PropsUIPage | PropsUIPrompt;
export declare type PropsUIText = PropsUITextTitle0 | PropsUITextTitle1 | PropsUITextTitle2 | PropsUITextTitle6 | PropsUITextBodyLarge;
export declare type PropsUIButton = PropsUIButtonPrimary | PropsUIButtonSecundary | PropsUIButtonForward | PropsUIButtonLabel;
export declare function isPropsUI(arg: any): arg is PropsUI;
export declare function isPropsUIText(arg: any): arg is PropsUIText;
export interface PropsUITextBodyLarge {
    __type__: 'PropsUITextBodyLarge';
    text: string;
    color?: string;
    margin?: string;
}
export declare function isPropsUITextBodyLarge(arg: any): arg is PropsUITextBodyLarge;
export interface PropsUITextBodyMedium {
    __type__: 'PropsUITextBodyMedium';
    text: string;
    color?: string;
    margin?: string;
}
export declare function isPropsUITextBodyMedium(arg: any): arg is PropsUITextBodyMedium;
export interface PropsUITextTitle0 {
    __type__: 'PropsUITextTitle0';
    text: string;
    color?: string;
    margin?: string;
}
export declare function isPropsUITextTitle0(arg: any): arg is PropsUITextTitle0;
export interface PropsUITextTitle1 {
    __type__: 'PropsUITextTitle1';
    text: string;
    color?: string;
    margin?: string;
}
export declare function isPropsUITextTitle1(arg: any): arg is PropsUITextTitle1;
export interface PropsUITextTitle2 {
    __type__: 'PropsUITextTitle2';
    text: string;
    color?: string;
    margin?: string;
}
export declare function isPropsUITextTitle2(arg: any): arg is PropsUITextTitle2;
export interface PropsUITextTitle6 {
    __type__: 'PropsUITextTitle6';
    text: string;
    color?: string;
    margin?: string;
}
export declare function isPropsUITextTitle6(arg: any): arg is PropsUITextTitle6;
export declare function isPropsUIButton(arg: any): arg is PropsUIButton;
export interface PropsUIButtonPrimary {
    __type__: 'PropsUIButtonPrimary';
    label: string;
    color?: string;
    onClick: () => void;
}
export declare function isPropsUIButtonPrimary(arg: any): arg is PropsUIButtonPrimary;
export interface PropsUIButtonSecundary {
    __type__: 'PropsUIButtonSecundary';
    label: string;
    color?: string;
    onClick: () => void;
}
export declare function isPropsUIButtonSecundary(arg: any): arg is PropsUIButtonSecundary;
export interface PropsUIButtonBack {
    __type__: 'PropsUIButtonBack';
    label: string;
    onClick: () => void;
}
export declare function isPropsUIButtonBack(arg: any): arg is PropsUIButtonBack;
export interface PropsUIButtonForward {
    __type__: 'PropsUIButtonForward';
    label: string;
    onClick: () => void;
}
export declare function isPropsUIButtonForward(arg: any): arg is PropsUIButtonForward;
export interface PropsUIButtonLabel {
    __type__: 'PropsUIButtonLabel';
    label: string;
    color?: string;
    onClick: () => void;
}
export declare function isPropsUIButtonLabel(arg: any): arg is PropsUIButtonLabel;
export interface PropsUIRadioItem {
    id: number;
    value: string;
    selected: boolean;
    onSelect: () => void;
}
export declare function isPropsUIRadioItem(arg: any): arg is PropsUIRadioItem;
export interface PropsUICheckBox {
    id: string;
    selected: boolean;
    onSelect: () => void;
}
export declare function isPropsUICheckBox(arg: any): arg is PropsUICheckBox;
export interface PropsUISpinner {
    __type__: 'PropsUISpinner';
    text: Text;
}
export declare function isPropsUISpinner(arg: any): arg is PropsUISpinner;
export interface PropsUIHeader {
    __type__: 'PropsUIHeader';
    title: Text;
}
export declare function isPropsUIHeader(arg: any): arg is PropsUIHeader;
export interface PropsUITable {
    __type__: 'PropsUITable';
    id: string;
    head: PropsUITableHead;
    body: PropsUITableBody;
    readOnly?: boolean;
    pageSize?: number;
}
export declare function isPropsUITable(arg: any): arg is PropsUITable;
export interface PropsUITableHead {
    __type__: 'PropsUITableHead';
    cells: PropsUITableCell[];
}
export declare function isPropsUITableHead(arg: any): arg is PropsUITableHead;
export interface PropsUITableBody {
    __type__: 'PropsUITableBody';
    rows: PropsUITableRow[];
}
export declare function isPropsUITableBody(arg: any): arg is PropsUITableBody;
export interface PropsUITableRow {
    __type__: 'PropsUITableRow';
    id: string;
    cells: PropsUITableCell[];
}
export declare function isPropsUITableRow(arg: any): arg is PropsUITableRow;
export interface PropsUITableCell {
    __type__: 'PropsUITableCell';
    text: string;
}
export declare function isPropsUITableCell(arg: any): arg is PropsUITableCell;
export interface PropsUISearchBar {
    __type__: 'PropsUISearchBar';
    placeholder: string;
    debounce?: number;
    onSearch: (words: string[]) => void;
}
export declare function isPropsUISearchBar(arg: any): arg is PropsUISearchBar;
export declare type Text = Translatable | string;
export declare function isText(arg: any): arg is Text;
export interface Translatable {
    translations: {
        [locale: string]: string;
    };
}
export declare function isTranslatable(arg: any): arg is Translatable;